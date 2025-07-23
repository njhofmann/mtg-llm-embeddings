import pickle
import dataclasses
from typing import Optional
import argparse
import time
import math
import time

import numpy as np
from numpy.linalg import norm
import requests

import paths


def search_scryfall(query_string, all_cards):
    if not query_string:
        return all_cards

    def add_cards(query_string, page):
        time.sleep(0.05)
        params = {'q': f'-set_type:funny game:paper format:edh {query_string}',
                    'page': page}
        response = requests.get('https://api.scryfall.com/cards/search',
                                headers={'User-Agent': 'MTGEmbeddings/1.0',
                                            'Accept': '*/*'},
                                params=params)
        response.raise_for_status()
        response_json = response.json()
        if warnings := response_json.get('warnings'):
            for warning in warnings:
                print(warning)  # TODO warning

        # TODO split cards as env var
        card_info = [(card['name'], card['scryfall_uri'])
                        for card in response_json['data']]
        n_cards_in_request = len(card_info)
        total_n_cards = response_json['total_cards'] if page == 1 else None
        return card_info, n_cards_in_request, total_n_cards

    def search_request(query_string):
        return lambda x: add_cards(query_string, x)

    result_cards = []
    search_func = search_request(query_string)
    card_info, n_cards_in_request, total_n_cards = search_func(1)
    result_cards += card_info
    n_next_pages = \
        math.ceil((total_n_cards - n_cards_in_request) / n_cards_in_request)
        
    print(f'total {total_n_cards} cards across {n_next_pages + 1} pages')

    next_pages = range(2, n_next_pages + 2)
    if n_next_pages < 4:
        for page in next_pages:
            result_cards += search_func(page)[0]
    else:
        import concurrent.futures
        n_workers = min(32, n_next_pages)
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
            submitted_urls \
                = [executor.submit(search_func, page) for page in next_pages]
            for future in concurrent.futures.as_completed(submitted_urls):
                result_cards += future.result()[0]

    print(f'retrieved {len(result_cards)} cards')
    return result_cards


@dataclasses.dataclass()
class LinkedList:
    name: str
    similarity: float
    url: str
    prev: Optional['LinkedList'] = None
    next: Optional['LinkedList'] = None


class MostSimilarManager:
    def __init__(self, max_len, most_or_least_similar):
        if max_len < 1:
            raise ValueError('n must be >= 1')
        self.max_len = max_len
        self.head = None
        self.tail = None
        self.most_or_least_similar = most_or_least_similar
        self.count = 0

    def add(self, name, similarity, url):
        if self.head is None:
            self.count += 1
            self.head = LinkedList(name, similarity, url)
            self.tail = self.head

        cur = self.head
        while cur is not None:
            if (self.most_or_least_similar and similarity > cur.similarity) \
                    or (not self.most_or_least_similar and similarity < cur.similarity):
                new_cur = LinkedList(name, similarity, url)
                new_cur.next = cur
                new_cur.prev = cur.prev
                if new_cur.prev:
                    new_cur.prev.next = new_cur
                cur.prev = new_cur

                if new_cur.prev is None:
                    self.head = new_cur

                if self.count < self.max_len:
                    self.count += 1
                else:
                    self.tail = self.tail.prev
                    self.tail.next = None
                break
            cur = cur.next

    def __str__(self):
        items = self.to_list()
        longest_name = max(len(x[0]) for x in items)
        s = ''
        for (name, sim, url) in items:
            spaces = ' ' * (longest_name - len(name))
            s += f'{name}{spaces} {sim:2f} {url}\n'
        return s

    def to_list(self):
        a = []
        cur = self.head
        while cur is not None:
            a.append((cur.name, cur.similarity, cur.url))
            cur = cur.next
        return a


def find_most_similar(conditioning_card_names, most_or_least_similar, n, scryfall_query, bench):
    global EMBEDDING_INFO

    print(f'conditioning cards {conditioning_card_names}')

    def measure(a, b):
        return float(np.dot(a, b) / (norm(a) * norm(b)))

    embeddings = paths.get_embeddings()

    if bench:
        search_start_time = time.perf_counter()

    target_embedding = np.sum(list(embeddings[card] for card in conditioning_card_names), axis=0) 

    manager = MostSimilarManager(n, most_or_least_similar)
    matching_cards = search_scryfall(scryfall_query, EMBEDDING_INFO.keys())

    if bench:
        print(f'query search took {time.perf_counter() - search_start_time}')

    if bench:
        embedding_start_time = time.perf_counter()

    for (card_name, url) in matching_cards:
        if card_name not in conditioning_card_names:
            if card_name not in EMBEDDING_INFO:
                # TODO add logging
                print(f'warning: card found in query "{card_name}" not in dataset,'
                      'ignoring for now')
                continue

            match = measure(embeddings[card_name], target_embedding)
            manager.add(card_name, match, url)

    if bench:
        print(f'emebdding took {time.perf_counter() - embedding_start_time}')

    print(manager)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=20, required=False)
    parser.add_argument('--card', '-c', type=str, action='extend', nargs='+', required=False)
    parser.add_argument('--query', '-q', required=False,
                        default=None, nargs='+')
    parser.add_argument('--least-sim', '-l', action='store_false')
    parser.add_argument('--bench', '-b', action='store_true')
    parser.add_argument('--continuous', '-o', action='store_true',
                        help='keep "the server" running, if given card & query args are ignored and taken from user input')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    if args.continuous:
        while True:
            target_card = input('target card: ')
            query = input('search query: ')
            print('searching...')
            find_most_similar(conditioning_card_name=[target_card],
                              most_or_least_similar=True,
                              n=20,
                              scryfall_query=query,
                              bench=args.bench)

    else:
        if args.card is None:
            raise ValueError('cards arg required for non-continuous search')
        print(args.card)
        query = ' '.join(args.query) if args.query else None
        find_most_similar(conditioning_card_names=args.card,
                          most_or_least_similar=args.least_sim,
                          n=args.n,
                          scryfall_query=query,
                          bench=args.bench)

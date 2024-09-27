import pickle
import dataclasses
from typing import Optional
import argparse

import numpy as np 
from numpy.linalg import norm
import requests

import paths


def search_scryfall(query_string, all_cards):
    if not query_string:
        for card in all_cards:
            yield card, None
    else:
        def add_cards(url, params):
            response = requests.get(url,
                                    headers={'User-Agent': 'MTGEmbeddings/1.0',
                                            'Accept': '*/*'},
                                    params=params)
            response.raise_for_status()
            response_json = response.json()
            if warnings := response_json.get('warnings'):
                for warning in warnings:
                    print(warning)
            for card in response_json['data']:
                for name in card['name'].split(' // '):
                    yield (name, card['scryfall_uri'])
            yield response_json
        
        url = 'https://api.scryfall.com/cards/search'
        params = {'q': f'-set_type:funny game:paper format:edh {query_string}'}
        while True:
            for item in add_cards(url, params):
                if isinstance(item, tuple):
                    yield item
            if not item.get('has_more', False):
                break
            url = item['next_page']
            params = None


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

    def print(self):
        items = self.to_list()
        longest_name = max(len(x[0]) for x in items)
        for (name, sim, url) in items:
            spaces = ' ' * (longest_name - len(name))
            print(f'{name}{spaces} {sim:2f} {url}')

    def to_list(self):
        a = []
        cur = self.head
        while cur is not None:
            a.append((cur.name, cur.similarity, cur.url))
            cur = cur.next
        return a


def find_most_similar(card_name, measure, most_or_least_similar, n, scryfall_query):
    match measure:
        case 'euclid':
            most_or_least_similar = not most_or_least_similar
            measure = lambda a, b: float(norm(np.array(a) - np.array(b)))
        case 'cos':
            measure = lambda a, b: float(np.dot(a, b) / (norm(a) * norm(b)))
        case _:
            raise ValueError(f'{measure} is unsupported measure')

    with open(paths.EMBEDDINGS_FILE, 'rb') as f:
        embeddings_info = pickle.load(f)

    target_embedding = embeddings_info[card_name]
    manager = MostSimilarManager(n, most_or_least_similar)
    for (queried_card_name, url) in search_scryfall(scryfall_query, embeddings_info.keys()):
        if card_name != queried_card_name:
            manager.add(queried_card_name, measure(embeddings_info[queried_card_name], target_embedding), url)

    manager.print()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=20, required=False)
    parser.add_argument('--card', '-c', type=str, nargs='+', required=True)
    parser.add_argument('--query', '-q', required=False, default=None, nargs='+')
    parser.add_argument('--least-sim', '-l', action='store_false')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    card = ' '.join(args.card)
    query = ' '.join(args.query) if args.query else None
    find_most_similar(card_name=card,
                      measure='cos',
                      most_or_least_similar=args.least_sim,
                      n=args.n,
                      scryfall_query=query)

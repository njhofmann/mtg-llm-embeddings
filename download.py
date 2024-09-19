import requests 
import json
import pathlib
import re
import uuid


REQUIRED_KEYS = ['cmc', 'colors', 'loyalty', 'defense', 'mana_cost', 'power', 'loyalty', 'toughness', 'name', 'oracle_text', 'type_line']
REQUIRED_TYPES = ['Artifact', 'Enchantment', 'Creature', 'Planeswalker', 'Land', 'Instant', 'Sorcery', 'Battle', 'Kindred']
UNACCEPTED_TYPES = ['Token', 'Vanguard', 'Hero', 'Ongoing']
DIMENSIONS = 512

DATA_DIRC = pathlib.Path('data')
DATA_DIRC.mkdir(parents=True, exist_ok=True)
RAW_CARDS = DATA_DIRC / 'raw_cards.json'
PROCESSED_CARDS = DATA_DIRC / 'processed_cards.jsonl'
BATCH_CARDS = DATA_DIRC / 'batch_requests.jsonl'


def process_type_line(type_line):
    if type_line is None:
        return None

    type_line = [t for t in type_line.split(' ') if t != '—']
    if any(t in REQUIRED_TYPES for t in type_line) and all(t not in UNACCEPTED_TYPES for t in type_line):  # TODO ifx this
        return type_line

    return None


def process_raw_card_json(card_data, related_cards):
    card_info = {key: card_data.get(key) for key in REQUIRED_KEYS}
    
    cmc = card_info['cmc']
    if cmc:  # double faced cards are null
        assert float(int(cmc)) == cmc

    if cmc:
        card_info['mana_value'] = int(cmc)
    elif card_info['mana_cost']:
        mana_parts = [part for part in re.split('}|{', card_info['mana_cost']) if part]
        while len(mana_parts) > 0 and mana_parts[0] == 'X':
            mana_parts = mana_parts[1:]
        
        value = 0
        if len(mana_parts) > 0:
            try:
                value = int(mana_parts[0])
            except ValueError:
                pass

        card_info['mana_value'] = value + len(mana_parts[1:])
    else:
        card_info['mana_value'] = None

    type_line = process_type_line(card_info['type_line'])
    if not type_line:
        return None

    card_info['types'] = list(sorted(type_line))

    # remove reminder text
    card_info['text'] = "".join(re.split(" \(|\)|\[|\]", card_info['oracle_text'])[::2])
    card_info['related'] = related_cards

    del card_info['type_line']
    del card_info['oracle_text']
    del card_info['cmc']
    return card_info


def main():
    if not RAW_CARDS.exists():
        response = requests.get('https://data.scryfall.io/oracle-cards/oracle-cards-20240917090203.json')
        response.raise_for_status()
        with open(RAW_CARDS, 'w') as f:
            raw_cards = json.dump(response.json(), f)
    else:
        cards = []
        longest_card = None
        with open(RAW_CARDS, 'r') as f:
            for card in json.load(f):
                if card['set_type'] =='funny' or 'rebalanced' in card.get('promo_types', []) \
                        or 'alchemy' in card.get('promo_types', []) or card['layout'] in ('double_faced_token', 'token'):
                    continue

                card_faces = card['card_faces'] if 'card_faces' in card else [card]
                related_cards = [related_card['name'] for related_card in card.get('all_parts', []) \
                                if process_type_line(related_card['type_line'])]
                for card_face in card_faces:
                    cur_related_cards = [card_face['name'] for related_card in related_cards if card_face['name'] not in related_card ]
                    if (processed_card := process_raw_card_json(card_face, cur_related_cards)):
                        str_card = str(processed_card)
                        if longest_card is None or len(str_card) > len(longest_card):
                            longest_card = str_card
                        cards.append(processed_card)

        print(f'processed {len(cards)} cards')
        print(longest_card)

        def get_batch_request_dict(card_json):
            return {"custom_id": f"{uuid.uuid4()}", 
                    "method": "POST", 
                    "url": "/v1/embeddings", 
                    "body": {"model": "text-embedding-3-large", 
                            "input": card_json,
                            "dimensions": DIMENSIONS}}


        def write_processed_card(json_file_writer, batch_file_writer, card):
            card_json = json.dumps(card, sort_keys=True)
            json_file_writer.write(f'{card_json}\n')
            batch_request_json = json.dumps(get_batch_request_dict(card_json))
            batch_file_writer.write(f'{batch_request_json}\n')
            return card_json
        

        try:
            card_file_writer = open(PROCESSED_CARDS, 'w')
            batch_file_writer = open(BATCH_CARDS, 'w')
            cards = list(map(lambda c: write_processed_card(card_file_writer, batch_file_writer, c), cards))
        finally:
            card_file_writer.close()
            batch_file_writer.close()


if __name__ == '__main__':
    main()

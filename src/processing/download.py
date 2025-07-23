import requests 
import json
import re
import argparse

import paths


REQUIRED_KEYS = ['cmc', 'colors', 'loyalty', 'defense', 'mana_cost', 'power', 'loyalty', 'toughness', 'name', 'oracle_text', 'type_line']
REQUIRED_TYPES = ['Artifact', 'Enchantment', 'Creature', 'Planeswalker', 'Land', 'Instant', 'Sorcery', 'Battle', 'Kindred']
UNACCEPTED_TYPES = ['Token', 'Vanguard', 'Hero', 'Ongoing']
DEFAULT_DIMENSIONS = 128    
TARGET_EMBEDDING_MODEL = 'text-embedding-3-large'
# TODO how to autogenerate this
SCRYFALL_URI = 'https://data.scryfall.io/oracle-cards/oracle-cards-20240924210259.json' 


def process_type_line(type_line):
    if type_line is None:
        return None

    type_line = [t for t in type_line.split(' ') if t != '—']
    if any(t in REQUIRED_TYPES for t in type_line) and all(t not in UNACCEPTED_TYPES for t in type_line):
        return type_line

    return None


def process_raw_card_json(card_data, related_cards):
    card_info = {key: card_data.get(key) for key in REQUIRED_KEYS}
    
    cmc = card_info['cmc']
    if cmc:  # double faced cards are null
        assert float(int(cmc)) == cmc

    if cmc:
        card_info['mana_value'] = int(cmc)
    elif card_info['mana_cost']:  # TODO if double face fill in colors
        mana_parts = [part for part in re.split('}|{', card_info['mana_cost']) if part]
        while len(mana_parts) > 0 and mana_parts[0] == 'X':
            mana_parts = mana_parts[1:]
        
        value = 0
        if len(mana_parts) > 0:
            try:
                value = int(mana_parts[0])
                mana_parts = mana_parts[1:]
            except ValueError:
                pass

        card_info['mana_value'] = value + len(mana_parts)
    else:
        card_info['mana_value'] = None

    if card_info.get('colors') is None:
        mana_parts = [part for part in re.split('}|{', card_info['mana_cost']) if part]
        colors = set()
        for color in 'WUBRG':
            for part in mana_parts:
                if color in part:
                    colors.add(color)
        card_info['colors'] = list(colors)

    card_info['colors'] = ''.join(sorted(card_info['colors'])) if card_info['colors'] else 'C'

    type_line = process_type_line(card_info['type_line'])
    if not type_line:
        return None

    card_info['types'] = list(sorted(type_line))

    # remove reminder text
    # TODO if multicard - join oracle text
    card_info['text'] = "".join(re.split(" \(|\)|\[|\]", card_info['oracle_text'])[::2])
    card_info['related'] = related_cards

    del card_info['type_line']
    del card_info['oracle_text']
    del card_info['cmc']
    return card_info


def main(dimensions: int, split_double_face_cards: bool):
    # TODO autogenerate check to redo batch run
    if not paths.RAW_CARDS.exists():
        response = requests.get(SCRYFALL_URI)
        response.raise_for_status()
        with open(paths.RAW_CARDS, 'w') as f:
            json.dump(response.json(), f)

    cards = []
    card_names = set()
    with open(paths.RAW_CARDS, 'r') as f:
        for card in json.load(f):
            if card['set_type'] =='funny' \
                or 'rebalanced' in card.get('promo_types', []) \
                    or 'alchemy' in card.get('promo_types', []) \
                        or card['layout'] in ('double_faced_token', 'token') \
                            or card['set_name'] == 'Battle the Horde':
                continue

            card_faces = card['card_faces'] if 'card_faces' in card and split_double_face_cards else [card]
            related_cards = [related_card['name'] for related_card in card.get('all_parts', []) \
                                if process_type_line(related_card['type_line'])]
            for card_face in card_faces:
                cur_related_cards = [card_face['name'] for related_card in related_cards if card_face['name'] not in related_card ]
                if (processed_card := process_raw_card_json(card_face, cur_related_cards)):
                    if processed_card['name'] in card_names:
                        raise RuntimeError(f'duplicate card name: {processed_card['name']}')
                    card_names.add(processed_card['name'])
                    cards.append(processed_card)

    print(f'processed {len(cards)} cards')

    def get_batch_request_dict(card_json):
        return {"custom_id": f"{card_json['name']}", 
                "method": "POST", 
                "url": "/v1/embeddings", 
                "body": {"model": TARGET_EMBEDDING_MODEL, 
                        "input": json.dumps(card_json),
                        "dimensions": dimensions}}


    def write_processed_card(json_file_writer, batch_file_writer, card):
        json_file_writer.write(f'{json.dumps(card, sort_keys=True)}\n')
        batch_file_writer.write(f'{json.dumps(get_batch_request_dict(card))}\n')
    

    try:
        card_file_writer = open(paths.PROCESSED_CARDS, 'w')
        batch_file_writer = open(paths.BATCH_CARDS, 'w')
        list(map(lambda c: write_processed_card(card_file_writer, batch_file_writer, c), cards))
    finally:
        card_file_writer.close()
        batch_file_writer.close()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dimensions', '-d', type=int, default=DEFAULT_DIMENSIONS, nargs=1)
    parser.add_argument('--split-multi-cards', '-s', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    main(args.dimensions, args.split_multi_cards)   

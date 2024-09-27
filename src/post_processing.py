import paths
import json
import pickle
import numpy as np
import numpy.linalg as norm
import typing
 

def post_processing_2():
    names_to_embeddings = {}
    with open(paths.RESPONSE_FILE, 'r') as f:
        for response_json in f.readlines():
            response_json = json.loads(response_json)
            names_to_embeddings[response_json['custom_id']] = response_json['response']['body']['data'][0]['embedding']

    card_jsons = {}
    with open(paths.PROCESSED_CARDS, 'r') as f:
        for card_json in f.readlines():
            card_json = json.loads(card_json)
            card_json['embedding'] = names_to_embeddings[card_json['name']]
            card_jsons[card_json['name']] = card_json

    with open(paths.EMBEDDINGS_INFO_FILE, 'wb') as f:
        pickle.dump(card_jsons, f)


def post_processing():
    names_to_embeddings = {}
    with open(paths.RESPONSE_FILE, 'r') as f:
        for (i, response_json) in enumerate(f.readlines()):
            response_json = json.loads(response_json)
            names_to_embeddings[response_json['custom_id']] = response_json['response']['body']['data'][0]['embedding']
    
    with open(paths.EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(names_to_embeddings, f)


if __name__ == '__main__':
    post_processing()

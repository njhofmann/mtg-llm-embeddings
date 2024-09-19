from batch import RESPONSE_FILE, RESPONSE_DIRC
from download import BATCH_CARDS
import json
import pickle
import numpy as np
import numpy.linalg as norm

EMBEDDINGS_FILE = RESPONSE_DIRC / 'embeddings.npy'
EMBEDDINGS_INDEX_FILE = RESPONSE_DIRC / 'card_index.pkl'

embeddings = []
ids = {}
with open(RESPONSE_FILE, 'r') as f:
    for (i, reponse) in enumerate(f.readlines()):
        response = json.loads(reponse)
        ids[response['custom_id']] = i
        embeddings.append(response['response']['body']['data'][0]['embedding'])

np.save(EMBEDDINGS_FILE, np.array(embeddings))

with open(BATCH_CARDS, 'r') as f:
    requests = [json.loads(request) for request in f.readlines()]

requests_info = [(json.loads(request['body']['input'])['name'], request['custom_id']) for request in requests]
card_name_idxs = {card_name: ids[custom_id] for (card_name, custom_id) in requests_info}

with open(EMBEDDINGS_INDEX_FILE, 'wb') as f:
    pickle.dump(card_name_idxs, f)

print(card_name_idxs['Unquenchable Fury'])
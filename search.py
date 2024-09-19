import numpy as np 
from numpy.linalg import norm
from gather_embeddings import EMBEDDINGS_FILE, EMBEDDINGS_INDEX_FILE
import pickle

with open(EMBEDDINGS_INDEX_FILE, 'rb') as f:
    embeddings_index = pickle.load(f)
    index_to_cards = {v: k for (k, v) in embeddings_index.items()}
    print(index_to_cards[3276])


card = 'Ponder'
target_index = embeddings_index[card]

def cos_sim(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

embeddings = np.load(EMBEDDINGS_FILE)
cosines = [(index_to_cards[i], cos_sim(embeddings[target_index], embedding)) for (i, embedding) in enumerate(embeddings) if i != target_index and i != 3277]

sorted_cosines = sorted(cosines, reverse=True, key=lambda x: x[1])
print(sorted_cosines[:10])
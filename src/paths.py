import pathlib as pl
import pickle

DATA_DIRC = pl.Path('data')
DATA_DIRC.mkdir(parents=True, exist_ok=True)
RAW_CARDS = DATA_DIRC / 'raw_cards.json'
PROCESSED_CARDS = DATA_DIRC / 'processed_cards.jsonl'
BATCH_CARDS = DATA_DIRC / 'batch_requests.jsonl'

BATCH_ID_FILE = 'batch_id.txt'
RESPONSE_DIRC = pl.Path('results')
RESPONSE_FILE = RESPONSE_DIRC / 'reponses.jsonl'
ERROR_FILE = RESPONSE_DIRC / 'error.jsonl'

EMBEDDINGS_FILE = RESPONSE_DIRC / 'embeddings.pkl'

EMBEDDING_INFO = None

def get_embeddings():
    global EMBEDDING_INFO
    if EMBEDDING_INFO is None:
        with open(EMBEDDINGS_FILE, 'rb') as f:
            EMBEDDING_INFO = pickle.load(f)
    return EMBEDDING_INFO
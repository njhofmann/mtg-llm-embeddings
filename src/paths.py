import pathlib as pl

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
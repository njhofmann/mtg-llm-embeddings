import paths
import numpy

def deck_list_to_embeddings(deck_list):
    with open(deck_list, 'r') as f:
        for line in f.readlines():
    cards = deck_list
    return numpy.array([paths.get_embeddings()[card] for card in cards])

def compare_decks(deck_list_a, deck_list_b):
    a = deck_list_to_embeddings(deck_list_a)
    b = deck_list_to_embeddings(deck_list_b)
    assert a.shape == b.shape
    n = len(deck_list_a)
    c = numpy.sum(a @ a.T) / n ** 2
    d = numpy.sum(b @ b.T) / n ** 2
    e = numpy.sum(a @ b.T) / n **2
    return c + d - (2 * e)


a = ['Ponder', 'Brainstorm', 'Counterspell', 'Remand']
b = ['Cryptic Command', 'Remand', 'Memory Lapse', 'Counterspell']
c = ['Thoughtseize', 'Murder', 'Snuff Out', 'Duress']
mmd = compare_decks(a, c)
print(mmd)
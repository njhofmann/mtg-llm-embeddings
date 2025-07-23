from download import main as download
from create_embeddings import main as create_embeddings
from post_processing import main as post_processing


if __name__ == '__main__':
    download(dimensions=512, split_double_face_cards=False)
    create_embeddings(action='create')
    post_processing()
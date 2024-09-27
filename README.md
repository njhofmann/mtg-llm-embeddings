# Setup

1. Have Python 3.12 installed, install packages with `pip install -r requirements.txt`
    1. Recommend setting up with venv or similar tooling
1. Download compressed embeddings from [here](https://drive.google.com/file/d/18MytGt1olSOHPB4d6s7psue6qT6ymgW2/view?usp=sharing), unzip the resulting pickle file to `results/embeddings.pkl`
1. run `python src/search -c <card_name> -q <scryfall_query>` to list the cards given Scryfall query (`-q`) that are most similar to the card given under `-c`
    1. [Scryfall syntax guide](https://scryfall.com/docs/syntax)
    1. `python src/search -h` for all supported arguments

  [Screencastfrom2024-09-2714-03-46-ezgif.com-video-to-gif-converter.webm](https://github.com/user-attachments/assets/d304fdf5-835b-43d8-84b6-fa1c338594a1)

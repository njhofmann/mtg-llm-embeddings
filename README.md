# Setup

1. Have Python 3.12 installed, install packages with `pip install -r requirements.txt`
    1. Recommend setting up with venv or similar tooling
1. Download compressed embeddings from [here](https://drive.google.com/file/d/18MytGt1olSOHPB4d6s7psue6qT6ymgW2/view?usp=sharing), unzip the resulting pickle file to `results/embeddings.pkl`
1. run `python src/search -c <card_name> -q <scryfall_query>` to list the cards given Scryfall query (`-q`) that are most similar to the card given under `-c`
    1. [Scryfall syntax guide](https://scryfall.com/docs/syntax)
    1. `python src/search -h` for all supported arguments


<video width="630" height="300" src="https://imgur.com/a/ubLAomJ"></video>

    

Project using an [LLM embedding model](https://platform.openai.com/docs/guides/embeddings/embedding-models) to create [embeddings](https://huggingface.co/blog/getting-started-with-embeddings) for every known MTG card (almost). Then using a [similarity measure](https://en.wikipedia.org/wiki/Similarity_measure) to sort cards in a given [Scryfall](https://scryfall.com/docs/syntax) query by their "closeness" to a given target card. 

In plain English think of this project saying "what cards in this category of cards are most like a target card"?

# Examples
- which black instant with mana value equal to 2 is most like [Path to Exile](https://scryfall.com/card/otc/85/path-to-exile) --> [Eliminate](https://scryfall.com/card/m21/97/eliminate?utm_source=api)
    - `python src/search.py -c Path to Exile -q cmc=2 t:instant c=b`
- which red enchantment is most like [Rhystic Study]([https://scryfall.com/card/otc/85/path-to-exile](https://scryfall.com/card/jmp/169/rhystic-study)) --> [Knowledge and Power]([https://scryfall.com/card/m21/97/eliminate?utm_source=api](https://scryfall.com/card/jou/101/knowledge-and-power?utm_source=api))
    - `python src/search.py -c Rhystic Study -q c=r t:enchantment`

# Setup
1. Have Python 3.12 installed, install packages with `pip install -r requirements.txt`
    1. Recommend setting up with venv or similar tooling
1. Download compressed embeddings from [here](https://drive.google.com/file/d/18MytGt1olSOHPB4d6s7psue6qT6ymgW2/view?usp=sharing), unzip the resulting pickle file to `results/embeddings.pkl`
1. run `python src/search -c <card_name> -q <scryfall_query>` to list the cards given Scryfall query (`-q`) that are most similar to the card given under `-c`
    1. [Scryfall syntax guide](https://scryfall.com/docs/syntax)
    1. `python src/search -h` for all supported arguments

  [Screencastfrom2024-09-2714-03-46-ezgif.com-video-to-gif-converter.webm](https://github.com/user-attachments/assets/d304fdf5-835b-43d8-84b6-fa1c338594a1)

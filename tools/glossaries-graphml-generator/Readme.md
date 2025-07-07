## Getting started

```bash
pip install networkx sentence-transformers spacy pyyaml
python -m spacy download en_core_web_sm
```

## Run
```bash
python main.py \
  --input ../storage/normalized/ \
  --output output/rail_glossary.graphml
```

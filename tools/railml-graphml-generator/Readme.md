## Project Structure

```bash
railml-graphml-generator/
│
├── schema_parser.py       # Parse railML XSDs for nodes & relationships
├── doc_extractor.py       # Extract human-readable descriptions from HTML/JS
├── graph_builder.py       # Build and export the GraphML file
├── cli.py                 # Command-line interface wrapper
├── utils/                 # Shared helpers (e.g., file handling, text cleaning)
├── data/
│   ├── railML-3.3-SR1/    # Input: official schema and documentation
│   └── intermediate/      # Optional cache (json/txt) for LLM prompts
└── output/
    └── rail_infrastructure.graphml
```

---

##  Getting started

### Supported Flags:
```text
--input: Path to the railML-3.3-SR1 root folder
--output: Destination .graphml file
--llm: Optional flag to enable future LLM-based enhancements
```

### Example Usage:
```bash
python cli.py --input ./data/railML-3.3-SR1 --output ./output/rail_infrastructure.graphml
```
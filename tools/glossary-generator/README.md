# Glossary .graphml File Generator

## Overview

This tool generates a `.graphml` file that encapsulates a graph of railway industry-specific terms, jargon, and abbreviations, 
along with their definitions and interconnections. The `.graphml` format, an XML-based structure, is chosen for its ability to represent 
relationships between terms efficiently. This approach ensures a universal, scalable, and easily updatable repository of domain knowledge, 
which is essential for enriching the contextual understanding of language models tailored to industrial applications.
The resulting `.graphml` file is designed for future integration into the **PathRAG pipeline** within the **MCP server**, 
a system dedicated to managing and querying industrial data. This enables advanced retrieval and analysis of railway terminology for various use cases.

## Technologies Used

The generator leverages several Python libraries, each serving a specific purpose in processing glossary data and constructing the graph:

- **NetworkX**: A powerful library for creating, manipulating, and analyzing graph structures. It forms the backbone of this tool by building and managing the graph of terms and their relationships.
- **Sentence Transformers**: Provides pre-trained transformer models to generate semantic embeddings of text. Here, it is used to compute similarity scores between term definitions, aiding in deduplication.
- **spaCy**: An advanced natural language processing (NLP) library offering features like tokenization and named entity recognition (NER). It extracts entities from definitions to establish meaningful connections between terms.
- **PyYAML**: A YAML parsing library for Python. It processes the metadata headers in raw glossary files, ensuring structured data extraction.
- **scikit-learn**: A machine learning library that includes clustering algorithms. The **Agglomerative Clustering** method is applied to group similar definitions, reducing redundancy in the graph.

## Installation

To use this tool, set up your environment by installing the required dependencies and downloading the necessary NLP model.

1. **Install Dependencies**:

   ```bash
   pip install networkx sentence-transformers spacy pyyaml scikit-learn
   ```

   These libraries collectively enable graph creation, text embedding, NLP processing, YAML parsing, and clustering.

2. **Download spaCy Model**:

   ```bash
   python -m spacy download en_core_web_lg
   ```

   The `en_core_web_lg` model is a small English language model for spaCy, providing efficient tokenization and entity recognition. Larger models can be used for improved accuracy if needed.

## Usage

Run the generator from the command line with the following syntax:

```bash
python .\tools\rail-glossary-generator\main.py \
  --input .\data\raw\glossaries\ \
  --output .\data\generated\rail-glossary.graphml
```

- **`--input`**: Specifies the directory containing raw glossary `.txt` files.
- **`--output`**: Defines the path where the generated `.graphml` file will be saved.

The script processes all `.txt` files in the input directory, constructs the graph, and exports it to the specified output location.

## Raw Glossary File Format

Raw glossary files are plain text files with a structured format: a YAML metadata header followed by term-definition pairs.

### File Structure

```
---
title: "Railway Terminology"
sourceName: "Railway Industry Association"
sourceUrl: "https://www.ria.org/glossary"
regions:
  - "GB"
lastUpdated: "2025-07-06"
collectedBy: "J. Doe"
---

Locomotive — A self-propelled vehicle used for pulling trains.
```

#### YAML Header

The header is enclosed between `---` markers and contains metadata in YAML format:

- **`title`**: The name of the document, article, or source material (e.g., "Glossary of Terms").
- **`sourceName`**: A descriptive name of the external source (e.g., a company or organization website).
- **`sourceUrl`**: A URL linking to the original source for reference or verification.
- **`regions`**: A list of ISO country codes (e.g., "US", "CA") indicating where the glossary is relevant.
- **`lastUpdated`**: The date of the most recent update in `YYYY-MM-DD` format.
- **`collectedBy`**: The name of the individual who compiled the glossary.

#### Term-Definition Pairs

Below the header, each line represents a single term or abbreviation and its definition, separated by an em dash (` — `). For example:

- `Locomotive — A self-propelled vehicle used for pulling trains` defines "Locomotive" as a term related to a specific railway system.

## Graph Construction Process

The tool follows these steps to transform raw glossary files into a `.graphml` graph:

1. **File Parsing**: Scans the input directory for `.txt` files, extracts YAML metadata, and parses term-definition pairs.
2. **Node Creation**: Adds each term as a node in the graph, with attributes like definition, source metadata, and a unique ID.
3. **Semantic Deduplication**: Uses Sentence Transformers to generate embeddings of definitions and applies Agglomerative Clustering to identify similar entries. Variants are linked with "variant_of" edges.
4. **Relationship Linking**: Employs spaCy to detect named entities in definitions, connecting terms that share entities with "related_to" edges.
5. **Export**: Saves the graph as a `.graphml` file using NetworkX, ready for use in other systems.

## Handling Duplicates

Given the diverse sources of glossary data, terms may appear multiple times with varying definitions. The tool employs 
a sophisticated approach to handle duplicates, ensuring the graph remains concise yet comprehensive:

- **Context-Dependent Duplicates**: When a term has distinct meanings depending on the context (e.g., "track" as a physical railway component versus a monitoring system), each meaning is preserved as a separate node in the graph. These nodes may be linked with "related_to" edges if they share relevant entities, maintaining their contextual distinctions.
- **Semantically Similar Duplicates**: When definitions of a term are similar but differ slightly in wording (e.g., "Locomotive: A vehicle that pulls trains" versus "Locomotive: A self-propelled train engine"), the tool uses **Sentence Transformers** to generate semantic embeddings of the definitions. These embeddings are clustered using **Agglomerative Clustering** with a cosine similarity threshold (default: 0.9). Similar definitions are merged into a single representative node, with other nodes linked to it via "variant_of" edges to indicate equivalence.

This dual approach ensures that meaningful variations are retained while redundant rephrasings are consolidated, optimizing the graph for both accuracy and efficiency.

## Customization Options

- **Similarity Threshold**: Adjust the `SIMILARITY_THRESHOLD` variable in `main.py` (default: 0.9) to control deduplication sensitivity. Lower values increase clustering strictness.
- **NLP Model**: Replace `en_core_web_sm` with a larger spaCy model for enhanced entity recognition accuracy.

## Future Enhancements

- **Multilingual Support**: Add compatibility with non-English glossaries by integrating appropriate NLP models.
- **Advanced Linking**: Incorporate dependency parsing or knowledge graph techniques for richer term relationships.
- **Visualization**: Include options to export graph visualizations (e.g., using Matplotlib or Graphviz) for user exploration.

## License

This project is licensed under the Apache License v2. See the [LICENSE](../../LICENSE) file for details.
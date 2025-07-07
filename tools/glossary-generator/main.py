import argparse
import networkx as nx
from pathlib import Path
import uuid
from collections import defaultdict
from sentence_transformers import SentenceTransformer
import spacy
import yaml
import re
import numpy as np
from sklearn.cluster import AgglomerativeClustering

# === NLP и embedding-модель ===
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

SIMILARITY_THRESHOLD = 0.9


def parse_glossary_file(filepath: Path):
    """Parse YAML header and rows in format: TERM — DEFINITION"""
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    # === Фаза 1: Определяем YAML-блок ===
    if not lines or lines[0].strip() != '---':
        raise ValueError(f"ERROR: YAML header must start with '---' in {filepath.name}")

    yaml_lines = []
    body_lines = []
    inside_yaml = True

    for line in lines[1:]:
        if inside_yaml:
            if line.strip() == '---':
                inside_yaml = False
            else:
                yaml_lines.append(line)
        else:
            body_lines.append(line)

    if inside_yaml:
        raise ValueError(f"ERROR:\tMissing closing '---' for YAML header in {filepath.name}")

    try:
        meta = yaml.safe_load("".join(yaml_lines))
    except yaml.YAMLError as e:
        raise ValueError(f"ERROR:\tYAML parsing failed in {filepath.name}: {e}")

    # === Фаза 2: Парсинг тела ===
    entries = []
    for line in body_lines:
        if not line.strip() or "—" not in line:
            continue
        term, definition = map(str.strip, line.split("—", 1))
        entries.append((term, definition))

    return meta, entries


def build_graph(input_dir: Path, output_file: Path):
    G = nx.MultiDiGraph()
    all_definitions = []
    all_nodes = []

    print(f"INFO:\tScanning {input_dir} for glossary files...")
    for file in input_dir.rglob("*.txt"):
        try:
            meta, entries = parse_glossary_file(file)
        except Exception as e:
            print(f"WARNING:\tFailed to parse {file.name}: {e}")
            continue

        for term, definition in entries:
            uid = str(uuid.uuid4())
            G.add_node(uid,
                       term=term,
                       definition=definition,
                       sourceName=meta.get("sourceName", file.stem),
                       sourceUrl=meta.get("sourceUrl", ""),
                       collectedBy=meta.get("collectedBy", ""),
                       lastUpdated=meta.get("lastUpdated", ""),
                       title=meta.get("title", ""),
                       regions=", ".join(meta.get("regions", [])))
            all_definitions.append(definition)
            all_nodes.append(uid)

    # === Семантическое схлопывание (кластеризация) ===
    print("INFO:\tSemantic deduplication via clustering...")
    embeddings = model.encode(all_definitions)
    clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=1 - SIMILARITY_THRESHOLD,
                                         metric='cosine', linkage='average')
    labels = clustering.fit_predict(embeddings)

    clustered = defaultdict(list)
    for label, uid in zip(labels, all_nodes):
        clustered[label].append(uid)

    for cluster_nodes in clustered.values():
        if len(cluster_nodes) <= 1:
            continue
        root = cluster_nodes[0]
        for other in cluster_nodes[1:]:
            G.add_edge(other, root, label="variant_of")

    # === NLP-связи ===
    print("INFO:\tLinking related definitions...")
    node_list = [(n, d) for n, d in G.nodes(data=True) if "definition" in d]
    for i, (nid1, data1) in enumerate(node_list):
        doc1 = nlp(data1["definition"])
        ents1 = {tok.text for tok in doc1.ents if tok.label_ in ("ORG", "PRODUCT", "EVENT", "GPE")}
        for j in range(i + 1, len(node_list)):
            nid2, data2 = node_list[j]
            if any(ent in data2["definition"] for ent in ents1):
                G.add_edge(nid1, nid2, label="related_to")

    # === Экспорт ===
    output_file.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(G, output_file)
    print(f"SUCCESS:\tGraph saved to {output_file}")


# === CLI ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .txt glossary files with headers to GraphML.")
    parser.add_argument("--input", "-i", required=True, help="Path to folder with .txt glossary files")
    parser.add_argument("--output", "-o", required=True, help="Output .graphml file path")

    args = parser.parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    if not input_path.exists() or not input_path.is_dir():
        print(f"ERROR:\tDirectory not found: {input_path}")
        exit(1)

    build_graph(input_path, output_path)

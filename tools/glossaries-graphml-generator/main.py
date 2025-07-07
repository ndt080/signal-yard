import argparse
import networkx as nx
from pathlib import Path
import uuid
from collections import defaultdict
from sentence_transformers import SentenceTransformer, util
import spacy
import yaml
import re

# === NLP и embedding-модель ===
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

SIMILARITY_THRESHOLD = 0.85

def parse_glossary_file(filepath: Path):
    """Парсит YAML header + строки формата TERM — DEFINITION"""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Разделяем header и тело
    header_match = re.match(r"^---\s*(.*?)\s*---\s*(.*)", content, re.DOTALL)
    if not header_match:
        raise ValueError(f"❌ Header not found in {filepath.name}")

    yaml_part, body = header_match.groups()
    meta = yaml.safe_load(yaml_part)

    entries = []
    for line in body.splitlines():
        if not line.strip() or "—" not in line:
            continue
        term, definition = map(str.strip, line.split("—", 1))
        entries.append((term, definition))

    return meta, entries

def build_graph(input_dir: Path, output_file: Path):
    G = nx.MultiDiGraph()
    term_nodes = defaultdict(list)

    print(f"📁 Scanning {input_dir} for glossary files...")
    for file in input_dir.rglob("*.txt"):
        try:
            meta, entries = parse_glossary_file(file)
        except Exception as e:
            print(f"⚠️ Failed to parse {file.name}: {e}")
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
            term_nodes[term].append((uid, definition))

    # === Семантическое схлопывание ===
    print("🔄 Semantic deduplication...")
    for term, nodes in term_nodes.items():
        if len(nodes) <= 1:
            continue

        embeddings = model.encode([d for _, d in nodes], convert_to_tensor=True)
        to_merge = {}
        for i in range(len(nodes)):
            if nodes[i][0] in to_merge:
                continue
            for j in range(i + 1, len(nodes)):
                if nodes[j][0] in to_merge:
                    continue
                score = util.cos_sim(embeddings[i], embeddings[j]).item()
                if score > SIMILARITY_THRESHOLD:
                    id_i, _ = nodes[i]
                    id_j, _ = nodes[j]
                    for u, v, k, data in list(G.in_edges(id_j, keys=True, data=True)):
                        G.add_edge(u, id_i, **data)
                    for u, v, k, data in list(G.out_edges(id_j, keys=True, data=True)):
                        G.add_edge(id_i, v, **data)
                    to_merge[id_j] = id_i
                    G.remove_node(id_j)

        remaining = [n[0] for n in nodes if n[0] not in to_merge]
        for i in range(len(remaining) - 1):
            G.add_edge(remaining[i], remaining[i + 1], label="variant_of")

    # === NLP-связи ===
    print("🔍 Linking related definitions...")
    node_list = [(n, d) for n, d in G.nodes(data=True) if "definition" in d]
    for i, (nid1, data1) in enumerate(node_list):
        doc1 = nlp(data1["definition"])
        for j in range(i + 1, len(node_list)):
            nid2, data2 = node_list[j]
            doc2 = nlp(data2["definition"])
            if any(tok.text in data2["definition"]
                   for tok in doc1.ents if tok.label_ in ("ORG", "PRODUCT", "EVENT", "GPE")):
                G.add_edge(nid1, nid2, label="related_to")

    # === Экспорт ===
    output_file.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(G, output_file)
    print(f"✅ Graph saved to {output_file}")

# === CLI ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .txt glossary files with headers to GraphML.")
    parser.add_argument("--input", "-i", required=True, help="Path to folder with .txt glossary files")
    parser.add_argument("--output", "-o", required=True, help="Output .graphml file path")

    args = parser.parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    if not input_path.exists() or not input_path.is_dir():
        print(f"❌ Directory not found: {input_path}")
        exit(1)

    build_graph(input_path, output_path)

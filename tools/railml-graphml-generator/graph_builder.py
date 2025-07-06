import networkx as nx
from typing import Dict
import os

def build_graph(elements: Dict[str, Dict], descriptions: Dict[str, str]) -> nx.DiGraph:
    G = nx.DiGraph()

    # Приводим описания к нижнему регистру для нормализации ключей
    normalized_descriptions = {k.lower(): v for k, v in descriptions.items()}

    for name, meta in elements.items():
        desc = normalized_descriptions.get(name.lower(), "")
        G.add_node(name,
                   description=desc,
                   elementType=meta.get("type", "unknown"),
                   railML_version="3.3 SR1")

    missing = [name for name in elements if name.lower() not in normalized_descriptions]
    print(f"⚠️ Missing descriptions for {len(missing)} elements (например: {missing[:5]})")

    # Добавляем ребра на основе children
    for source, meta in elements.items():
        for child in meta.get('children', []):
            if child in elements:
                G.add_edge(source, child, relation="part_of")

    return G

def export_graphml(graph: nx.DiGraph, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    nx.write_graphml(graph, output_path)
    print(f"Graph exported to: {output_path}")

if __name__ == "__main__":
    from schema_parser import parse_xsd_folder
    from doc_extractor import parse_documentation_folder

    schema_folder = "./data/railML-3.3-SR1/source/schema"
    doc_folder = "./data/railML-3.3-SR1/documentation/model"
    output_file = "./output/rail_infrastructure.graphml"

    elements = parse_xsd_folder(schema_folder)
    descriptions = parse_documentation_folder(doc_folder)

    graph = build_graph(elements, descriptions)
    export_graphml(graph, output_file)

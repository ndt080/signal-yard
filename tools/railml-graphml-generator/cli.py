import argparse
from schema_parser import parse_xsd_folder
from doc_extractor import parse_documentation_folder
from graph_builder import build_graph, export_graphml

def main():
    parser = argparse.ArgumentParser(description="Generate a GraphML from railML schema and docs")
    parser.add_argument("--input", required=True, help="Path to the railML root folder")
    parser.add_argument("--output", required=True, help="Path to output .graphml file")
    parser.add_argument("--llm", action="store_true", help="Enable LLM-assisted description cleanup")

    args = parser.parse_args()

    schema_path = f"{args.input}/source/schema"
    doc_path = f"{args.input}/documentation/model"

    print("Parsing schema...")
    elements = parse_xsd_folder(schema_path)

    print("Extracting descriptions...")
    descriptions = parse_documentation_folder(doc_path)

    if args.llm:
        print("[LLM mode] Enhancing descriptions — not implemented in this CLI yet")
        # Optional: integrate LLM processing here in future

    print("Building graph...")
    graph = build_graph(elements, descriptions)

    print("Exporting to GraphML...")
    export_graphml(graph, args.output)

if __name__ == "__main__":
    main()
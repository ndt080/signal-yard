import os
import xml.etree.ElementTree as ET
from typing import Dict, List

RAILML_NS = {
    'xs': 'http://www.w3.org/2001/XMLSchema'
}

def parse_complex_type(element: ET.Element) -> Dict[str, List[str]]:
    children = []
    attributes = []

    for child in element.findall('.//xs:element', RAILML_NS):
        name = child.get('name')
        if name:
            children.append(name)

    for attr in element.findall('.//xs:attribute', RAILML_NS):
        name = attr.get('name')
        if name:
            attributes.append(name)

    return {
        'children': children,
        'attributes': attributes
    }

def parse_xsd_elements(xsd_path: str) -> Dict[str, Dict]:
    tree = ET.parse(xsd_path)
    root = tree.getroot()
    elements = {}

    for element in root.findall('.//xs:element', RAILML_NS):
        name = element.get('name')
        type_ = element.get('type')
        if name:
            elements[name] = {
                'type': type_ or 'complex',
                'attributes': [],
                'children': []
            }

    for complex_type in root.findall('.//xs:complexType', RAILML_NS):
        parent_name = complex_type.get('name')
        structure = parse_complex_type(complex_type)

        if parent_name and parent_name in elements:
            elements[parent_name]['children'].extend(structure['children'])
            elements[parent_name]['attributes'].extend(structure['attributes'])

    return elements

def parse_xsd_folder(folder_path: str) -> Dict[str, Dict]:
    all_elements = {}

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xsd'):
                full_path = os.path.join(root, file)
                print(f"Parsing: {full_path}")
                elements = parse_xsd_elements(full_path)
                all_elements.update(elements)

    return all_elements

if __name__ == "__main__":
    input_folder = "./data/railML-3.3-SR1/source/schema/gml"
    elements = parse_xsd_folder(input_folder)

    print(f"Found {len(elements)} elements")
    for k, v in list(elements.items())[:10]:
        print(f"- {k}: {v}")
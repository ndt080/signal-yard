import os
from bs4 import BeautifulSoup
from typing import Dict
import re

def extract_descriptions_from_html(html_path: str) -> Dict[str, str]:
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    descriptions = {}

    # Example: find tooltip entries or label-description pairs
    for span in soup.find_all('span', {'class': 'tooltip'}):
        key = span.get('data-name') or span.text.strip()
        desc = span.get('title') or span.get('data-tooltip')
        if key and desc:
            descriptions[key] = desc

    # Fallback: scan paragraph blocks with potential class/type mentions
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        matches = re.findall(r'\b([A-Z][a-zA-Z0-9_]+)\b\s*[:\-–]\s*(.+)', text)
        for key, desc in matches:
            if key not in descriptions:
                descriptions[key] = desc

    return descriptions

def parse_documentation_folder(folder_path: str) -> Dict[str, str]:
    all_descriptions = {}

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.htm', '.html')):
                full_path = os.path.join(root, file)
                print(f"Extracting from: {full_path}")
                descs = extract_descriptions_from_html(full_path)
                all_descriptions.update(descs)

    return all_descriptions

if __name__ == "__main__":
    input_folder = "./data/railML-3.3-SR1/documentation/model"
    descriptions = parse_documentation_folder(input_folder)

    print(f"Found {len(descriptions)} descriptions")
    for k, v in list(descriptions.items())[:10]:
        print(f"- {k}: {v}")
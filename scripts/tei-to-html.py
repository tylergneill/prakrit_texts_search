import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Define the source and output directories
source_dir = Path('tei')
output_dir = Path('html')

# Namespace for TEI XML files
TEI_NAMESPACE = {'tei': 'http://www.tei-c.org/ns/1.0'}

def get_all_text(element):
    """Recursively gets all text from an element and its children."""
    text = []
    if element.text:
        text.append(element.text.strip())
    for child in element:
        text.append(get_all_text(child))
    if element.tail:
        text.append(element.tail.strip())
    return ' '.join(filter(None, text))

def process_xml_file(xml_path, output_path):
    """Parses a single TEI XML file and converts it to an HTML file."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # --- Remove all <note> elements before processing ---
        # We need to find the parents of the notes to remove them.
        for parent in root.findall('.//tei:*[tei:note]', TEI_NAMESPACE):
            for note in parent.findall('tei:note', TEI_NAMESPACE):
                parent.remove(note)

        # --- Extract Metadata ---
        title_element = root.find('.//tei:titleStmt/tei:title', TEI_NAMESPACE)
        author_element = root.find('.//tei:titleStmt/tei:author', TEI_NAMESPACE)
        
        html_title = title_element.text if title_element is not None else xml_path.stem
        author_name = author_element.text if author_element is not None else "Unknown Author"

        # --- Extract Content ---
        body_content = []
        body_content.append(f"<h1>{html_title}</h1>")
        body_content.append(f"<h2>by {author_name}</h2>")

        text_element = root.find('tei:text', TEI_NAMESPACE)
        if text_element is not None:
            # Find all relevant content tags (p and l)
            for elem in text_element.iter():
                tag_name = elem.tag.split('}')[-1] # Remove namespace for comparison
                if tag_name in ['l', 'p']:
                    full_text = get_all_text(elem)
                    if full_text:
                        body_content.append(f"<p>{full_text}</p>")

        # --- Create HTML ---
        if len(body_content) <= 2: # Only h1 and h2 were added
            # This is now expected for some files, so we won't print a warning.
            return

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        joined_body = '\n'.join(body_content)

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{html_title}</title>
</head>
<body data-pagefind-body>
{joined_body}
</body>
</html>
"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    except ET.ParseError as e:
        print(f"Error parsing {xml_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred with {xml_path}: {e}")

def main():
    """Main function to find and process all XML files."""
    print(f"Starting conversion from '{source_dir}' to '{output_dir}'...")
    
    # Ensure the base output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    processed_count = 0
    for xml_file in source_dir.rglob('*.xml'):
        relative_path = xml_file.relative_to(source_dir)
        html_file_path = output_dir / relative_path.with_suffix('.html')
        process_xml_file(xml_file, html_file_path)
        processed_count += 1
        
    print(f"Conversion process finished. Processed {processed_count} files.")

if __name__ == "__main__":
    main()
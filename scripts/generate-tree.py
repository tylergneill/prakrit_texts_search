import os
from pathlib import Path

def generate_tree_string(startpath):
    """Generates a string representation of a directory tree and counts files."""
    tree_lines = []
    startpath = Path(startpath)
    
    # Get all paths, ignoring .DS_Store files
    all_paths = [p for p in startpath.rglob('*') if p.name != '.DS_Store']
    paths = sorted(all_paths, key=lambda p: str(p).lower())
    
    # Count only the files
    file_count = sum(1 for p in paths if p.is_file())

    dir_structure = {str(p): [] for p in paths if p.is_dir()}
    dir_structure[str(startpath)] = []

    for path in paths:
        parent = str(path.parent)
        if parent in dir_structure:
            dir_structure[parent].append(path)

    def build_tree(dir_path, prefix=""):
        """Recursively builds the tree string."""
        contents = sorted(dir_structure.get(str(dir_path), []), key=lambda p: str(p).lower())
        for i, path in enumerate(contents):
            is_last = i == (len(contents) - 1)
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{path.name}")
            if path.is_dir():
                new_prefix = prefix + ("    " if is_last else "│   ")
                build_tree(path, new_prefix)

    tree_lines.append(f"{startpath.name}/")
    build_tree(startpath)
    return "\n".join(tree_lines), file_count


def main():
    """Main function to generate the tree and write to an HTML file."""
    tei_dir = Path('tei')
    output_file = Path('docs/tei_structure.html')
    
    print(f"Generating directory tree for: {tei_dir}")
    tree_diagram_str, file_count = generate_tree_string(tei_dir)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory Structure of TEI</title>
    <style>
        body {{ font-family: monospace; background-color: #f4f4f4; color: #333; padding: 2em; }}
        pre {{ background-color: #fff; padding: 1.5em; border-radius: 5px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>Directory Structure of <code>tei/</code></h1>
    <p>Total files: {file_count}</p>
    <pre>{tree_diagram_str}</pre>
</body>
</html>
"""
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html_content, encoding='utf-8')
    print(f"Successfully created HTML diagram at: {output_file}")

if __name__ == "__main__":
    main()
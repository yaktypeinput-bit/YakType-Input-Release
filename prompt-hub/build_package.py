import os
import json
import re
from datetime import datetime

def parse_frontmatter(content):
    """
    Parses YAML-like frontmatter between '---' delimiters.
    Returns (metadata_dict, remaining_content).
    """
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content
    
    meta_str, actual_content = match.groups()
    metadata = {}
    for line in meta_str.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    
    return metadata, actual_content.strip()

def generate_package():
    # Since the script is now inside prompt-hub, 
    # the search directory is the same as the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_hub_dir = script_dir
    output_file = os.path.join(script_dir, "..", "prompt-package.json")
    
    if not os.path.exists(prompt_hub_dir):
        print(f"Error: Directory '{prompt_hub_dir}' not found.")
        return

    package = {
        "version": "1.0",
        "id": "com.yaktype.release.standard",
        "displayName": "YakType 官方提示词包",
        "author": "YakType Team",
        "description": "来自 YakType-Input-Release 的官方标准提示词集合。",
        "updatedAt": datetime.now().isoformat() + "Z",
        "prompts": []
    }

    # Use os.walk to recursively find markdown files
    for root, dirs, files in os.walk(prompt_hub_dir):
        for filename in files:
            if filename.endswith(".md") and filename != "README.md":
                filepath = os.path.join(root, filename)
                
                # Model name is the parent directory name (if not prompt-hub itself)
                parent_dir = os.path.basename(root)
                model_name = parent_dir if parent_dir != prompt_hub_dir else "General"
                
                with open(filepath, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    if not file_content:
                        continue
                    
                    metadata, content = parse_frontmatter(file_content)
                    
                    # Extract title from content if meta name is missing
                    if "name" not in metadata:
                        first_line = content.splitlines()[0].strip() if content.splitlines() else ""
                        name = first_line.lstrip("# ").strip() if first_line.startswith("#") else filename
                    else:
                        name = metadata["name"]
                    
                    # UUID from metadata is mandatory for stable tracking
                    # If missing, fallback to filename-based ID (but warn)
                    prompt_id = metadata.get("uuid")
                    if not prompt_id:
                        print(f"Warning: Missing 'uuid' in metadata for {filepath}. Using filename-based ID.")
                        prompt_id = os.path.splitext(filename)[0]
                    
                    # Use model from metadata if present, otherwise from folder name
                    model = metadata.get("model", model_name)
                    
                    # Add version if present (useful for tracking updates)
                    version = metadata.get("version", "1.0")
                    
                    package["prompts"].append({
                        "id": prompt_id,
                        "name": name,
                        "model": model,
                        "version": version,
                        "content": content
                    })

    # Sort prompts by name for consistency
    package["prompts"].sort(key=lambda x: x["name"])

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(package, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully generated {output_file} with {len(package['prompts'])} prompts.")

if __name__ == "__main__":
    generate_package()

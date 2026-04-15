import os
import json
from datetime import datetime

def generate_package():
    prompt_hub_dir = "prompt-hub"
    output_file = "prompt-package.json"
    
    if not os.path.exists(prompt_hub_dir):
        print(f"Error: Directory '{prompt_hub_dir}' not found.")
        return

    package = {
        "version": "1.0",
        "id": "com.yaktype.release.standard",
        "displayName": "YakType 官方提示词包",
        "author": "YakType Team",
        "description": "来自 YakType-Release 的官方标准提示词集合。",
        "updatedAt": datetime.now().isoformat() + "Z",
        "prompts": []
    }

    for filename in os.listdir(prompt_hub_dir):
        if filename.endswith(".md") and filename != "README.md":
            filepath = os.path.join(prompt_hub_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if not lines:
                    continue
                
                # Extract title from first line (# Title)
                first_line = lines[0].strip()
                name = first_line.lstrip("# ").strip() if first_line.startswith("#") else filename
                
                # Content is the whole file (or we could strip the title, but keeping it is safer for markdown)
                content = "".join(lines).strip()
                
                prompt_id = os.path.splitext(filename)[0]
                
                package["prompts"].append({
                    "id": prompt_id,
                    "name": name,
                    "content": content
                })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(package, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully generated {output_file} with {len(package['prompts'])} prompts.")

if __name__ == "__main__":
    generate_package()

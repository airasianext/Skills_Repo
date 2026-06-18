# split_dataset_template.py
# Reference implementation for partitioning large ADK Golden datasets into rate-limit safe chunks.

import json
import os
import sys

def split_dataset(source_json_path, output_directory, chunk_size=11):
    """
    Slices a large Golden evaluation dataset into rate-limit safe chunks.
    Default chunk_size is 11, keeping parallel model/metrics calls well under 50.
    """
    if not os.path.exists(source_json_path):
        print(f"❌ Source file not found: {source_json_path}")
        return
        
    os.makedirs(output_directory, exist_ok=True)
    
    with open(source_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    eval_cases = data.get("eval_cases", [])
    total_cases = len(eval_cases)
    print(f"📋 Loaded golden evaluation set with {total_cases} total cases.")
    
    # Calculate slices
    slices = []
    for i in range(0, total_cases, chunk_size):
        suffix = f"part{(i // chunk_size) + 1}"
        slices.append((i, min(i + chunk_size, total_cases), suffix))
        
    for start, end, suffix in slices:
        chunk_cases = eval_cases[start:end]
        part_data = {
            "eval_set_id": f"{data.get('eval_set_id')}_{suffix}",
            "name": f"{data.get('name')} - Part {suffix[-1]}",
            "description": f"{data.get('description')} (Chunk {suffix})",
            "eval_cases": chunk_cases
        }
        
        output_filename = f"legacy_eval_{suffix}.test.json"
        output_path = os.path.join(output_directory, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(part_data, out, indent=2, ensure_ascii=False)
            
        print(f"✅ Created {output_filename} containing {len(chunk_cases)} cases (indices {start} to {end-1}).")

if __name__ == "__main__":

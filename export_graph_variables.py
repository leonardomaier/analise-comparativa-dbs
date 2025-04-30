import os
import re
import json
import subprocess
import pandas as pd

result_dirs = [
    "./web/pg/1800_seconds_duration/60_seconds_ramp/100_threads/insert_workload",
    "./web/pg/1800_seconds_duration/60_seconds_ramp/100_threads/mixed_workload",
    "./web/pg/1800_seconds_duration/60_seconds_ramp/100_threads/read_workload",
    "./web/pg/1800_seconds_duration/60_seconds_ramp/100_threads/update_workload",
    
    "./web/pg/1800_seconds_duration/120_seconds_ramp/200_threads/insert_workload",
    "./web/pg/1800_seconds_duration/120_seconds_ramp/200_threads/mixed_workload",
    "./web/pg/1800_seconds_duration/120_seconds_ramp/200_threads/read_workload",
    "./web/pg/1800_seconds_duration/120_seconds_ramp/200_threads/update_workload",
    
    "./web/pg/1800_seconds_duration/240_seconds_ramp/400_threads/insert_workload",
    "./web/pg/1800_seconds_duration/240_seconds_ramp/400_threads/mixed_workload",
    "./web/pg/1800_seconds_duration/240_seconds_ramp/400_threads/read_workload",
    "./web/pg/1800_seconds_duration/240_seconds_ramp/400_threads/update_workload",
    
    "./web/mongo/1800_seconds_duration/60_seconds_ramp/100_threads/insert_workload",
    "./web/mongo/1800_seconds_duration/60_seconds_ramp/100_threads/mixed_workload",
    "./web/mongo/1800_seconds_duration/60_seconds_ramp/100_threads/read_workload",
    "./web/mongo/1800_seconds_duration/60_seconds_ramp/100_threads/update_workload",
    
    "./web/mongo/1800_seconds_duration/120_seconds_ramp/200_threads/insert_workload",
    "./web/mongo/1800_seconds_duration/120_seconds_ramp/200_threads/mixed_workload",
    "./web/mongo/1800_seconds_duration/120_seconds_ramp/200_threads/read_workload",
    "./web/mongo/1800_seconds_duration/120_seconds_ramp/200_threads/update_workload",
    
    "./web/mongo/1800_seconds_duration/240_seconds_ramp/400_threads/insert_workload",
    "./web/mongo/1800_seconds_duration/240_seconds_ramp/400_threads/mixed_workload",
    "./web/mongo/1800_seconds_duration/240_seconds_ramp/400_threads/read_workload",
    "./web/mongo/1800_seconds_duration/240_seconds_ramp/400_threads/update_workload",
]

def get_json_files():
    for dir_path in result_dirs:
        graph_file_path = os.path.join(dir_path, "content", "js", "graph.js")
        new_graph_file_path = os.path.join(dir_path, "content", "js", "graph_cleaned.js")
        
        print(f"Processing {graph_file_path}...")

        if os.path.exists(graph_file_path):
            print(f"Found {graph_file_path}.")
            with open(graph_file_path, "r") as file:
                content = file.read()
            
            # Extract variables and keep only the data property, ensuring proper closing brackets
            cleaned_content = "\n".join(
                "var {} = {{ data: {{ {} }} }};".format(match.group(1), match.group(2).rstrip("}]") + "}]}")
                for match in re.finditer(
                    r"var\s+(\w+)\s*=\s*{\s*data\s*:\s*{\s*(.*?)\s*}\s*.*?};", content, re.DOTALL
                )
            )
            
            # Prepare Node.js imports and commands to create JSON files in the same directory
            node_imports = "const fs = require('fs');\n\n"
            node_commands = ""
            for match in re.finditer(r"var\s+(\w+)\s*=", cleaned_content):
                variable_name = match.group(1)
                json_file_path = os.path.join(dir_path, f"{variable_name}.json").replace("\\", "/")
                node_commands += f"""
    fs.writeFileSync('{json_file_path}', JSON.stringify({variable_name}));"""

            # Write the imports, cleaned content, and Node.js commands to the new file
            with open(new_graph_file_path, "w") as new_file:
                new_file.write(node_imports)
                new_file.write(cleaned_content)
                new_file.write("\n")
                new_file.write(node_commands)

            subprocess.run(["node", new_graph_file_path], check=True)

get_json_files()
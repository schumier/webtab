# import json
# import ast

# with open("D:\\Project\\pbix\\Human Resources Sample PBIX\\Report\\Layout", encoding="utf-8", errors="ignore") as f:
#     raw = f.read()
    
#     cleaned = raw.replace('\\"', '"').replace('\\\\', '\\').replace("'", '"')

#     # cleaned2 = ast.literal_eval(cleaned)


#     json_str = json.dumps(cleaned)
#     parsed = json.loads(json_str)
#     # pretty = json.dumps(parsed, indent=4)

# with open("D:\\Project\\pbix\\data.json", "w") as file:
#     json.dump(parsed, file, indent=4)

import json

# Example of a malformed JSON string (single quotes, no double quotes)
malformed = "{'name': 'Alice', 'age': 30, 'is_student': False}"

# 1. Clean up: Convert to Python dict safely
# Use ast.literal_eval for simple cases (not recommended for untrusted input!)
import ast

try:
    with open("D:\\Project\\pbix\\Human Resources Sample PBIX\\Report\\Layout", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
        python_dict = ast.literal_eval(raw)
except Exception as e:
    print("Error parsing:", e)
    python_dict = {}

# 2. Save as valid JSON to a file
with open("D:\\Project\\pbix\\data.json", 'w') as f:
    json.dump(python_dict, f, indent=4)
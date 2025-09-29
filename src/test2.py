import json

# Read potentially malformed JSON from a file
with open("D:\\Project\\pbix\\Human Resources Sample PBIX\\Report\\Layout", 'r') as f:
    raw = f.read()

# Remove null bytes if present
raw = raw.replace('\x00', '')

# Try to parse JSON safely
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"JSONDecodeError: {e}")
    # Optionally, handle or repair the JSON here
    # For demo purposes, exit if error
    data = None

# If parsing succeeded, save cleaned JSON to a new file
if data is not None:
    with open("D:\\Project\\pbix\\data.json", 'w') as f:
        json.dump(data, f, indent=4)
    print("Cleaned JSON saved to cleaned.json")
else:
    print("Could not parse JSON after cleanup.")
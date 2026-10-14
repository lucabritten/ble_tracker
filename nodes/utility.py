import json

def load_from_json(file_path: str, *field_path: str):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            
            current = data
            
            for field in field_path:
                if isinstance(current, dict) and field in current:
                    current = current[field]
                else:
                    print(f"Field path '{'.'.join(field_path)}' not found in {file_path}.")
                    return None
            
            return current
        
    except OSError:
        print(f"Config file {file_path} does not exist.")
        return None
    except ValueError:
        print(f"Error parsing JSON in {file_path}.")
        return None
    
def reverse_bytes(b: bytes) -> bytes:
    # Dreht ein Bytes-Objekt in MicroPython ohne slice-step -1 um
    return bytes(b[i] for i in range(len(b) - 1, -1, -1))
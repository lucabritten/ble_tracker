import json
import re

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

def is_mac_address(name) -> bool:
    """Checks if a string is a MAC-adress"""
    return bool(re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$").match(name))

def is_irk_address(irk) -> bool:
    """Checks if a string is a IRK-adress"""
    return bool(re.compile(r"^[0-9A-Fa-f]{32}$").match(irk))
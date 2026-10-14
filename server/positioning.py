def calculate_current_location(rssi_data: dict) -> str:
    if not rssi_data:
        return "Unknown"
    
    closest_room = max(rssi_data, key=rssi_data.get)
    max_rssi = rssi_data[closest_room]
    
    return closest_room
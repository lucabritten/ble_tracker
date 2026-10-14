import json
import network
import time

def load_wifi_credentials(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("network")
    except OSError:
        print(f"Config file {path} does not exist.")
        return None
    except ValueError:
        print(f"Error parsing JSON in {path}.")
        return None

def connect_to_wifi(credentials):
    if not credentials:
        print("Skipping connection: No valid credentials loaded.")
        return False
        
    wifi = network.WLAN(network.STA_IF)
    
    if not wifi.active():
        wifi.active(True)
        print("Activated WiFi interface.")
    
    if wifi.isconnected():
        wifi.disconnect()
    
    wifi.connect(credentials["wifi_name"], credentials["wifi_password"])
    print("Connecting to wifi...")
    
    timeout = 10
    while timeout > 0:
        if wifi.isconnected():
            return True
        time.sleep(1)
        timeout -= 1
        
    return False
    
def main():
    wifi_credentials = load_wifi_credentials("config/config.json")
    if connect_to_wifi(wifi_credentials):
        print("Successfully connected to configured Wifi.")
        print("Network configuration (IP, Subnet, Gateway, DNS):", network.WLAN(network.STA_IF).ifconfig())
    else:
        print("Wifi connection failed.")

if __name__ == "__main__":
    main()
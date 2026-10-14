import aioble
import ucryptolib

from utility import load_from_json, reverse_bytes

CONFIG_PATH = "config/config.json"

RAW_IRK = load_from_json(CONFIG_PATH, "tracked_device", "ble_irk")
GLOBAL_IRK_BYTES = None

if RAW_IRK:
    try:
        raw_bytes = bytes.fromhex(RAW_IRK)
        GLOBAL_IRK_BYTES = reverse_bytes(raw_bytes)
    except ValueError:
        print("Invalid IRK-Hex-format in config file.")
        

async def get_rssi_for_device():
    async with aioble.scan(duration_ms=5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device = result.device
            if device.addr and mac_belongs_to_tracked_device(device.addr):
                return result.rssi
    return None

def bluetooth_ah(irk_bytes: bytes, prand_bytes: bytes) -> bytes:
    padded_prand = b'\x00' * 13 + prand_bytes
    cipher = ucryptolib.aes(irk_bytes, 1)
    aes_result = cipher.encrypt(padded_prand)
    
    return aes_result[-3:]

def mac_belongs_to_tracked_device(mac_bytes: bytes):
    if len(mac_bytes) != 6 or not GLOBAL_IRK_BYTES:
        return False
    
    # If MAC-Adress is a Resolvable Private Address, then upper two bits ot the first
    # Byte needs to be binary '01'
    # Otherwise the MAC is no RPA -> does not belong to the tracked device
    if (mac_bytes[0] & 0xC0) != 0x40:
        return False
    
    mac_prand = mac_bytes[0:3]
    mac_hash = mac_bytes[3:6]
    
    calculated_hash = bluetooth_ah(GLOBAL_IRK_BYTES, mac_prand)
    
    return calculated_hash == mac_hash
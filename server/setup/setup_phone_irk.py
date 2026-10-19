import os
import subprocess
import time
import re
import configparser

from persistance import insert_tracked_device

BLUETOOTH_DIR = "/var/lib/bluetooth"

def run_cmd(cmd):
    """Runs a shell-command und returns the output"""
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return result.stdout.strip()


def get_existing_devices():
    """Collects all known device-folders"""
    devices = set()
    if os.path.exists(BLUETOOTH_DIR):
        for adapter in os.listdir(BLUETOOTH_DIR):
            adapter_path = os.path.join(BLUETOOTH_DIR, adapter)
            if os.path.isdir(adapter_path):
                for dev in os.listdir(adapter_path):
                    if is_mac_adress(dev):
                        devices.add(dev)
    
    return devices

def send_btctl(proc, cmd):
    """Sends a command to a running bluetoothctl-process"""
    proc.stdin.write(cmd + "\n")
    proc.stdin.flush()
    time.sleep(0.5)
    
def main():
    if os.getuid() != 0:
        print("[!] Rerun this script with admin previleges: sudo python3 setup_phone_irk.py")
        return
    
    print("=" * 60)
    print("     PHONE BLE IRK EXTRAKTOR & PAIRING ASSISTANT")
    print("=" * 60)
    
    old_devices = get_existing_devices()
    
    # Setup bluetooth-deamon
    print("\n[1/4] Starting Bluetooth-adapter/-agents...")
    subprocess.run("sudo rfkill unblock bluetooth", shell=True)
    subprocess.run("sudo systemctl restart bluetooth", shell=True)
    time.sleep(2)
    
    # Starting bluetoothctl as interactive process, to send commands live
    bt_proc = subprocess.Popen(
        ["bluetoothctl"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    send_btctl(bt_proc, "power on")
    send_btctl(bt_proc, "agent DisplayYesNo")
    send_btctl(bt_proc, "default-agent")
    send_btctl(bt_proc, "scan on")
    
    print("\n[2/4] Searching for nearby phones...")
    print("     Make sure that bluetooth is activated on your phone and that you're in the bluetooth settings.")
    
    start_scan = time.time()
    found_devices = {}
    
    while time.time() - start_scan < 10:
        devices_output = run_cmd("bluetoothctl devices")
        for line in devices_output.splitlines():
            match = re.match(r"Device\s+([0-9A-Fa-f:]+)\s+(.*)", line)
            if match:
                mac, name = match.groups()
                found_devices[name] = mac
        time.sleep(1)
    
    send_btctl(bt_proc, "scan off")
    
    if not found_devices:
        print("\n[-] Did not find any devices. Please restart bluetooth on your device.")
        bt_proc.terminate()
        return

    print("\Found Bluetooth-devices:")
    dev_list = list(found_devices.items())
    for idx, (name, mac) in enumerate(dev_list):
        print(f"  [{idx}] {name} ({mac})")
        
    # Users chooses his device:
    try:
        selected = int(input("\nEnter the number of your phone: "))
        selected_name, selected_mac = dev_list[selected]
    except (ValueError, IndexError):
        print("[-] Invalid input")
        bt_proc.terminate()
        return

    print(f"\n[3/4] Starting pairing with {selected_name} ({selected_mac})...")
    print("      -> There will be a code shown on your phone.")
    print("      -> Confirm the code on your phone and in the terminal with 'yes' (if asked).")

    # Pair device
    send_btctl(bt_proc, f"pair {selected_mac}")
    
    timeout = 45
    start_wait = time.time()
    paired_successfully = False
    
    while time.time() - start_wait < timeout:
        current_devices = get_existing_devices()
        new_ones = current_devices - old_devices
        if selected_mac in current_devices or new_ones:
            paired_successfully = True
            break
        
        try:
            bt_proc.stdin.write("yes\n")
            bt_proc.stdin.flush()
        except:
            pass
        
        time.sleep(2)
        print(".", end="", flush=True)
    
    bt_proc.terminate()
    print("\n")
    
    if not paired_successfully:
        print("[-] Pairing was not successfull. Please try again")
        return

    print(f"[+] Pairing with {selected_mac} was successfull")
    
    print("\n[4/4] Reading Identity Resolving Key (IRK)...")
    time.sleep(1)

    found_irk = None
    for adapter in os.listdir(BLUETOOTH_DIR):
        dev_info_path = os.path.join(BLUETOOTH_DIR, adapter, selected_mac, "info")
        if os.path.exists(dev_info_path):
            config = configparser.ConfigParser()
            config.optionxform = str
            config.read(dev_info_path)
            
            if config.has_section("IdentityResolvingKey") and config.has_option("IdentityResolvingKey", "Key"):
                found_irk = config.get("IdentityResolvingKey", "Key")
                break

    if found_irk:
        print("\n" + "=" * 60)
        print(f" SUCCESS! IRK of your phone:")
        print(f" -> {found_irk}")
        print("=" * 60)
        print("Please write this key to config/config.json\n")
        name = input("\nEnter the name of your phone: ")
        insert_tracked_device(selected_mac, name)
    else:
        print("[-] Paired to your device, but no IRK was found.")

if __name__ == "__main__":
    main()
    
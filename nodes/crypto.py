from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def bluetooth_ah(irk_bytes: bytes, prand_bytes: bytes) -> bytes:
    """
    Berechnet den Hash für eine BLE Resolvable Private Address (RPA)
    gemäß Bluetooth Core Specification (ah-Funktion).
    """
    padded_prand = b'\x00' * 13 + prand_bytes
    cipher = Cipher(algorithms.AES(irk_bytes), modes.ECB())
    encryptor = cipher.encryptor()
    aes_result = encryptor.update(padded_prand) + encryptor.finalize()
    return aes_result[-3:]

def check_rpa_mac_list(irk_bytes: bytes, mac_list: list):
    """
    Prüft eine Liste von MAC-Adressen gegen einen IRK und testet
    sowohl für den IRK als auch für die MAC jeweils die normale
    und die umgedrehte Byte-Reihenfolge.
    """
    # Die beiden IRK-Varianten (Normal vs. Umgedreht)
    irk_variants = [
        ("Normaler IRK", irk_bytes),
        ("Umgedrehter IRK", irk_bytes[::-1])
    ]
    
    for mac_str in mac_list:
        clean_hex = mac_str.replace(":", "").replace("-", "")
        if len(clean_hex) != 12:
            print(f"[-] Überspringe ungültige MAC-Länge: {mac_str}")
            continue
            
        mac_bytes = bytes.fromhex(clean_hex)
        
        # Die beiden MAC-Varianten (Normal vs. Umgedreht)
        mac_norm = mac_bytes
        mac_rev = mac_bytes[::-1]
        
        mac_variants = [
            ("MAC Normal (Big-Endian)", mac_norm[0:3], mac_norm[3:6]),
            ("MAC Umgedreht (Little-Endian)", mac_rev[0:3], mac_rev[3:6])
        ]
        
        match_found = False
        
        # Alle Kombinationen ausprobieren (2 IRK-Optionen x 2 MAC-Optionen = 4 Versuche)
        for irk_name, current_irk in irk_variants:
            for mac_name, prand, received_hash in mac_variants:
                calculated_hash = bluetooth_ah(current_irk, prand)
                
                if calculated_hash == received_hash:
                    print(f"[+] TREFFER gefunden für {mac_str}!")
                    print(f"    -> {irk_name} + {mac_name}")
                    print(f"    -> Prand: {prand.hex()} | Hash: {received_hash.hex()}")
                    match_found = True
                    # Optional: Nach erstem Treffer abbrechen per 'break', 
                    # falls man nur wissen will, ob es passt.
        
        if not match_found:
            print(f"[-] Keine Übereinstimmung für MAC: {mac_str}")
        print("-" * 50)

# ==========================================
# BEISPIEL-TESTLAUF
# ==========================================
if __name__ == "__main__":
    # Dein IRK (16 Bytes / 32 Hex-Zeichen)
    sample_irk = bytes.fromhex("78FE67595173438CFDEF5193D062E801")
    
    # Eine Liste von zu prüfenden MAC-Adressen (z.B. aus deinem BLE-Scan)
    mac_addresses = [
        "7d:97:03:f2:b0:58",
        "f8:df:ad:b8:f5:8b",
        "62:29:f1:31:fa:6b",
        "cb:45:26:40:47:22",
        "d8:fc:92:6a:fd:7b",
        "d5:40:52:fb:fd:63",
        "77:ff:75:f5:c9:cf",
        "46:5b:76:35:db:63",
        "41:f3:54:42:76:0d",
        "4d:58:91:c0:16:25",
        "69:a2:3f:5d:9d:cb",
        "67:05:2e:ca:d0:35",
        "ec:c2:df:9a:88:27"
    ]
    
    print(f"Starte Überprüfung von {len(mac_addresses)} MAC-Adressen...\n")
    check_rpa_mac_list(sample_irk, mac_addresses)
import machine
import onewire
import ds18x20
import time
import network
import socket
import ujson # MicroPython di solito usa ujson, ma json potrebbe funzionare su build recenti

# --- Configurazione WiFi ---
WIFI_SSID = "_TUO_SSID_WIFI_"
WIFI_PASSWORD = "TUA_PASSWORD_WIFI"

# --- Configurazione UDP (non OSC) ---
BROADCAST_IP = "192.168.1.255"  # O "255.255.255.255"
UDP_PORT = 64901                 # Scegli una porta (diversa da quella OSC se la usi per altro)
DEVICE_ID = "rp2040_sensor_1"   # Un ID per il tuo dispositivo

# --- Configurazione Sensore di Temperatura ---
ONE_WIRE_PIN = 26

# --- Funzione per la Connessione WiFi (invariata dalla versione OSC) ---
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connessione a WiFi SSID: {ssid}...")
        wlan.connect(ssid, password)
        max_wait = 15
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3: break
            max_wait -= 1; print("."); time.sleep(1)
    if wlan.isconnected():
        print("WiFi Connesso! IP:", wlan.ifconfig()[0])
        return wlan
    else:
        print("Connessione WiFi fallita."); return None

# --- Inizializzazione Sensore di Temperatura (invariata) ---
ds_sensor = None; target_rom = None; rom_hex_target = "N/A"
try:
    ow_pin = machine.Pin(ONE_WIRE_PIN)
    ow = onewire.OneWire(ow_pin)
    ds_sensor = ds18x20.DS18X20(ow)
    roms = ds_sensor.scan()
    if not roms: raise SystemExit("Sensore DS18B20 non trovato.")
    target_rom = roms[0]
    rom_hex_target = "".join(map(lambda x: f"{x:02x}", target_rom))
    print(f"Lettura temperatura da sensore: {rom_hex_target}")
except Exception as e:
    print(f"Errore inizializzazione sensore: {e}"); raise SystemExit("Errore sensore.")

# --- Connessione alla Rete ---
wlan_interface = connect_wifi(WIFI_SSID, WIFI_PASSWORD)

# --- Inizializzazione Socket UDP ---
udp_socket = None
if wlan_interface and wlan_interface.isconnected():
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Abilita broadcast
        print(f"Socket UDP configurato per inviare a {BROADCAST_IP}:{UDP_PORT}")
    except Exception as e:
        print(f"Errore creazione socket UDP: {e}"); udp_socket = None

# --- Ciclo Principale ---
if udp_socket and ds_sensor and target_rom:
    print(f"Avvio invio dati di temperatura via UDP JSON.")
    while True:
        try:
            if not wlan_interface.isconnected():
                print("WiFi disconnesso. Riconnessione..."); wlan_interface = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
                if not (wlan_interface and wlan_interface.isconnected()):
                    print("Riconnessione fallita."); time.sleep(10); continue
            
            ds_sensor.convert_temp()
            time.sleep_ms(100)
            temp_c = ds_sensor.read_temp(target_rom)
            
            if temp_c is None:
                print(f"Errore lettura temperatura.")
            else:
                print(f"Temperatura: {temp_c:.2f} °C -> Invio UDP JSON...")
                try:
                    # Crea il payload JSON
                    data_payload = {
                        "deviceId": DEVICE_ID,
                        "sensorId": rom_hex_target,
                        "temperature_celsius": round(temp_c, 2)
                    }
                    json_payload = ujson.dumps(data_payload)
                    
                    udp_socket.sendto(json_payload.encode('utf-8'), (BROADCAST_IP, UDP_PORT))
                    print(f"  Payload JSON inviato: {json_payload}")
                except Exception as e_sock:
                    print(f"Errore durante l'invio UDP: {e_sock}")
            
        except onewire.OneWireError as e: print(f"Errore OneWire: {e}."); time.sleep(2)
        except Exception as e: print(f"Errore nel ciclo: {e}"); time.sleep(5)
        time.sleep_ms(100) # Pausa per invio ogni ~5 secondi
else:
    if not udp_socket: print("Socket UDP non inizializzato.")
    if not (ds_sensor and target_rom): print("Inizializzazione sensore fallita.")

if udp_socket: udp_socket.close(); print("Socket UDP chiuso.")
print("Script terminato o interrotto.")
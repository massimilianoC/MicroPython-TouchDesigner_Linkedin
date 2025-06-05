# Invio Temperatura da Arduino Nano RP2040 a TouchDesigner via UDP JSON

Questo progetto dimostra come leggere i dati da un sensore di temperatura DS18B20 utilizzando un Arduino Nano RP2040 Connect con MicroPython e inviare questi dati in tempo reale a TouchDesigner tramite pacchetti UDP formattati in JSON. In TouchDesigner, i dati vengono ricevuti, parsati e possono essere utilizzati per controllare parametri visivi o altri processi (ad esempio, l'alpha di un oggetto, come suggerito dal nome del file di progetto).

## Componenti del Progetto

### Hardware Richiesto
* **Arduino Nano RP2040 Connect**
* **Sensore di temperatura DS18B20** (collegato al pin GP26 / A0 del Nano RP2040 Connect)
* Resistenza di pull-up da 4.7kΩ per il DS18B20 (se non già integrata nel modulo del sensore)
* Connessione a una rete WiFi locale

### Software Utilizzato
* **MicroPython** (firmware per l'Arduino Nano RP2040 Connect)
* **TouchDesigner**

## File nel Repository

1.  **`main.py`**
    * **Descrizione:** Script MicroPython da caricare sull'Arduino Nano RP2040 Connect.
    * **Funzionalità:**
        * Si connette alla rete WiFi specificata.
        * Inizializza e legge i dati dal sensore di temperatura DS18B20 collegato al pin `ONE_WIRE_PIN` (GP26).
        * Formatta i dati della temperatura (ID del dispositivo, ID del sensore, temperatura in Celsius) in una stringa JSON.
        * Invia la stringa JSON come pacchetto UDP in broadcast sulla rete locale.
    * **Configurazione:** Prima di eseguire, modifica le seguenti variabili all'inizio dello script:
        * `WIFI_SSID`: Il nome (SSID) della tua rete WiFi.
        * `WIFI_PASSWORD`: La password della tua rete WiFi.
        * `BROADCAST_IP`: L'indirizzo IP di broadcast della tua sottorete (es. "192.168.1.255" o "255.255.255.255").
        * `UDP_PORT`: La porta UDP su cui verranno inviati i messaggi (es. `64901`). Questa porta deve corrispondere a quella impostata nell'operatore `UDP In DAT` in TouchDesigner.
        * `DEVICE_ID`: Un identificatore per il tuo dispositivo.
        * `ONE_WIRE_PIN`: Il pin GPIO a cui è collegato il sensore DS18B20 (default: 26).

2.  **`DAT_execute.py`**
    * **Descrizione:** Script Python progettato per essere utilizzato all'interno di un operatore **`DAT Execute DAT`** in TouchDesigner.
    * **Funzionalità:**
        * Viene eseguito ogni volta che l'operatore `UDP In DAT` (monitorato) riceve nuovi dati.
        * Prende l'ultimo messaggio JSON ricevuto (la stringa di testo).
        * Parsa la stringa JSON per estrarre il valore della temperatura (specificamente, il valore associato alla chiave `"temperature_celsius"`).
        * Aggiorna un operatore **`Constant CHOP`** (nominato `temperatura_valore` nello script d'esempio) con il valore numerico della temperatura estratta. Questo rende la temperatura disponibile come un canale CHOP per ulteriori elaborazioni.
    * **Utilizzo in TouchDesigner:**
        * Crea un `DAT Execute DAT`.
        * Nel pannello dei parametri del `DAT Execute DAT`, collega l' `UDP In DAT` (che riceve i dati dal Nano) al campo "DAT" (nella prima scheda dei parametri).
        * Attiva il callback "Table Change" (o "Row Change" / "Cell Change").
        * Incolla il contenuto di `DAT_execute.py` nell'editor di testo del `DAT Execute DAT`.
        * Assicurati di avere un `Constant CHOP` nella tua rete TouchDesigner con il nome specificato in `NOME_CONSTANT_CHOP_TARGET` all'interno dello script (es. `temperatura_valore`).

3.  **`Json UDP Arduino Temp to Alpha.toe`** (File del Progetto TouchDesigner)
    * **Descrizione:** Il file di progetto TouchDesigner che implementa la ricezione, il parsing e l'utilizzo dei dati di temperatura.
    * **Componenti Chiave all'interno del Progetto (basati sull'immagine fornita):**
        * **`UDP In DAT` (es. `udpin1`):** Configurato per ascoltare sulla porta UDP specificata in `main.py` e ricevere i pacchetti JSON come stringhe di testo.
        * **`DAT Execute DAT` (es. `datexec1`):** Contiene lo script `DAT_execute.py` (o il suo contenuto) e monitora l' `UDP In DAT`. Quando nuovi dati arrivano, parsa il JSON e aggiorna:
        * **`Constant CHOP` (es. `constant1`, poi rinominato `tempc` tramite un `Rename CHOP`):** Questo CHOP ora contiene il valore numerico della temperatura come un canale.
        * **(Metodo Alternativo di Parsing JSON Visibile nell'Immagine):** L'immagine mostra anche l'uso di un operatore **`JSON DAT`** (es. `json1`) che prende l'input (forse dall' `UDP In DAT` o da un `Text DAT` intermedio) e usa un'espressione JSONPath (`$.temperature_celsius`) per estrarre direttamente il valore della temperatura in una tabella. L'output di questo `JSON DAT` può poi essere inviato a un `DAT to CHOP` per convertirlo in un segnale CHOP. Questo è un modo potente e spesso più semplice per gestire JSON semplici senza scripting Python esteso per il parsing.
        * **Catena di Elaborazione CHOP (es. `lag1`, `limit1`, `math1`, `speed1`, `lookup1`, `null1`):** Questi operatori CHOP vengono usati per elaborare ulteriormente il segnale di temperatura (smussarlo, limitarlo, scalarlo) per renderlo adatto a controllare altri parametri, come ad esempio un valore Alpha per la trasparenza.
        * **Visualizzazione (es. `CHOP to TOP`):** Per visualizzare il valore del canale CHOP risultante.

4.  **`TouchDesigner.jpg`**
    * **Descrizione:** Uno screenshot che illustra la rete di operatori all'interno del progetto TouchDesigner, mostrando come i dati UDP vengono ricevuti, elaborati e resi disponibili.

## Flusso di Lavoro del Progetto

1.  Il sensore DS18B20 misura la temperatura.
2.  Lo script `main.py` sull'Arduino Nano RP2040 Connect legge questo valore.
3.  Il Nano si connette al WiFi e invia i dati della temperatura (formattati come JSON) via UDP broadcast alla rete locale.
4.  In TouchDesigner, l'operatore `UDP In DAT` riceve questi pacchetti JSON.
5.  I dati JSON vengono parsati:
    * O tramite lo script Python nel `DAT Execute DAT` (contenuto di `DAT_execute.py`), che aggiorna un `Constant CHOP`.
    * O tramite l'operatore `JSON DAT` (come visibile nell'immagine), che estrae il valore in una tabella, la quale può essere poi convertita in un CHOP tramite un `DAT to CHOP`.
6.  Il valore numerico della temperatura è ora disponibile come un canale CHOP in TouchDesigner.
7.  Questo canale CHOP può essere ulteriormente elaborato (smussato, scalato, mappato) e utilizzato per controllare qualsiasi parametro in TouchDesigner (ad esempio, l'alpha di un materiale, la velocità di un'animazione, l'intensità di una luce, ecc.).

## Setup e Utilizzo

### Lato Arduino Nano RP2040 (MicroPython)
1.  Assicurati che il firmware MicroPython sia installato sul tuo Nano RP2040 Connect.
2.  Collega il sensore di temperatura DS18B20 al pin specificato in `ONE_WIRE_PIN` (default GP26/A0), con la necessaria resistenza di pull-up se non integrata.
3.  Apri il file `main.py` e modifica le variabili `WIFI_SSID`, `WIFI_PASSWORD`, `BROADCAST_IP`, e `UDP_PORT` con le tue impostazioni di rete.
4.  Carica `main.py` sul filesystem del Nano RP2040 Connect.
5.  Avvia (o resetta) la scheda per eseguire lo script. Controlla l'output della console seriale per messaggi di stato (connessione WiFi, lettura sensore, invio UDP).

### Lato TouchDesigner
1.  Apri il file di progetto `Json UDP Arduino Temp to Alpha.toe`.
2.  Localizza l'operatore `UDP In DAT` (es. `udpin1`).
3.  Nei parametri dell'`UDP In DAT`, assicurati che la **Port** corrisponda esattamente alla `UDP_PORT` che hai impostato nello script `main.py`.
4.  Esamina come lo script nel `DAT Execute DAT` (che usa il codice di `DAT_execute.py`) o l'operatore `JSON DAT` estraggono la temperatura.
5.  Il valore della temperatura dovrebbe apparire nel `Constant CHOP` (es. `tempc`) o nell'output del `DAT to CHOP` (se si usa il metodo `JSON DAT`).
6.  Ora puoi usare questo canale CHOP per pilotare altri parametri nel tuo progetto TouchDesigner.

## Note Aggiuntive
* Assicurati che il tuo computer con TouchDesigner e l'Arduino Nano RP2040 Connect siano sulla **stessa rete WiFi locale**.
* Il **firewall** sul tuo computer potrebbe bloccare i pacchetti UDP in entrata. Se non ricevi dati in TouchDesigner, controlla le impostazioni del tuo firewall e crea un'eccezione per TouchDesigner o per la porta UDP specifica, se necessario.
* L'**indirizzo IP di broadcast** corretto è importante. `255.255.255.255` è un tentativo generico, ma l'indirizzo di broadcast specifico della tua sottorete (es. `192.168.1.255` per una rete `192.168.1.x/24`) è solitamente più affidabile.
* Assicurati che la **chiave JSON** per la temperatura (es. `"temperature_celsius"`) sia esattamente la stessa nello script `main.py` (che crea il JSON) e nello script di parsing in TouchDesigner (contenuto in `DAT_execute.py` o nell'espressione JSONPath del `JSON DAT`).

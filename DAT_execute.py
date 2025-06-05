import json # TouchDesigner usa Python standard, quindi 'json' va bene

# Questo script viene eseguito quando il DAT specificato (il tuo UDP In DAT) cambia.
# 'dat' è una referenza all'UDP In DAT che ha triggerato l'esecuzione.
# 'table' è un alias per 'dat.table' per questo callback.

def onTableChange(dat):
    # Definisci il nome dell'operatore CHOP dove vuoi mettere il valore numerico della temperatura.
    # Creeremo un Constant CHOP con questo nome.
    NOME_CONSTANT_CHOP_TARGET = "temperatura_valore" # Puoi cambiare questo nome

    # Accedi all'operatore Constant CHOP. Se non esiste, crealo o gestisci l'errore.
    target_op = op(NOME_CONSTANT_CHOP_TARGET)
    if target_op is None:
        # debug(f"Attenzione: Operatore CHOP target '{NOME_CONSTANT_CHOP_TARGET}' non trovato. Creane uno (es. Constant CHOP).")
        # Potresti voler creare l'operatore qui se non esiste, ma è meglio farlo manualmente.
        return

    if dat.numRows > 0:
        # Prende l'ultimo messaggio ricevuto (ultima riga, colonna 'message')
        # L'UDP In DAT di default mette il messaggio nella prima colonna, il cui header è 'message'
        # Se hai cambiato il nome della colonna, aggiornalo qui.
        try:
            last_message_str = dat[dat.numRows - 1, 'message'].val
        except td.TDError: # Potrebbe succedere se la colonna 'message' non esiste
            # Se hai solo una colonna e non ha un header, usa l'indice 0
            last_message_str = dat[dat.numRows - 1, 0].val


        try:
            data_dict = json.loads(last_message_str)

            # Estrai la temperatura. Assicurati che la chiave "temperature_celsius"
            # corrisponda ESATTAMENTE a quella che invii dal MicroPython.
            temperature = data_dict.get("temperature_celsius") 

            if temperature is not None:
                # Scrivi il valore nel primo canale (parametro 'value0') del Constant CHOP.
                try:
                    target_op.par.value0 = float(temperature)
                    # debug(f"Temperatura aggiornata in '{NOME_CONSTANT_CHOP_TARGET}': {temperature}")
                except Exception as e_par:
                    # debug(f"Errore nell'impostare il parametro su '{NOME_CONSTANT_CHOP_TARGET}': {e_par}")
                    pass
            else:
                # debug(f"Chiave 'temperature_celsius' non trovata nel JSON ricevuto: {last_message_str}")
                pass
        except json.JSONDecodeError:
            # debug(f"Errore nel decodificare la stringa JSON: {last_message_str}")
            pass
        except Exception as e_script:
            # debug(f"Errore generico nello script onTableChange: {e_script}")
            pass
    returnimport json # TouchDesigner usa Python standard, quindi 'json' va bene

# Questo script viene eseguito quando il DAT specificato (il tuo UDP In DAT) cambia.
# 'dat' è una referenza all'UDP In DAT che ha triggerato l'esecuzione.
# 'table' è un alias per 'dat.table' per questo callback.

def onTableChange(dat):
    # Definisci il nome dell'operatore CHOP dove vuoi mettere il valore numerico della temperatura.
    # Creeremo un Constant CHOP con questo nome.
    NOME_CONSTANT_CHOP_TARGET = "temperatura_valore" # Puoi cambiare questo nome

    # Accedi all'operatore Constant CHOP. Se non esiste, crealo o gestisci l'errore.
    target_op = op(NOME_CONSTANT_CHOP_TARGET)
    if target_op is None:
        # debug(f"Attenzione: Operatore CHOP target '{NOME_CONSTANT_CHOP_TARGET}' non trovato. Creane uno (es. Constant CHOP).")
        # Potresti voler creare l'operatore qui se non esiste, ma è meglio farlo manualmente.
        return

    if dat.numRows > 0:
        # Prende l'ultimo messaggio ricevuto (ultima riga, colonna 'message')
        # L'UDP In DAT di default mette il messaggio nella prima colonna, il cui header è 'message'
        # Se hai cambiato il nome della colonna, aggiornalo qui.
        try:
            last_message_str = dat[dat.numRows - 1, 'message'].val
        except td.TDError: # Potrebbe succedere se la colonna 'message' non esiste
            # Se hai solo una colonna e non ha un header, usa l'indice 0
            last_message_str = dat[dat.numRows - 1, 0].val


        try:
            data_dict = json.loads(last_message_str)

            # Estrai la temperatura. Assicurati che la chiave "temperature_celsius"
            # corrisponda ESATTAMENTE a quella che invii dal MicroPython.
            temperature = data_dict.get("temperature_celsius") 

            if temperature is not None:
                # Scrivi il valore nel primo canale (parametro 'value0') del Constant CHOP.
                try:
                    target_op.par.value0 = float(temperature)
                    # debug(f"Temperatura aggiornata in '{NOME_CONSTANT_CHOP_TARGET}': {temperature}")
                except Exception as e_par:
                    # debug(f"Errore nell'impostare il parametro su '{NOME_CONSTANT_CHOP_TARGET}': {e_par}")
                    pass
            else:
                # debug(f"Chiave 'temperature_celsius' non trovata nel JSON ricevuto: {last_message_str}")
                pass
        except json.JSONDecodeError:
            # debug(f"Errore nel decodificare la stringa JSON: {last_message_str}")
            pass
        except Exception as e_script:
            # debug(f"Errore generico nello script onTableChange: {e_script}")
            pass
    return
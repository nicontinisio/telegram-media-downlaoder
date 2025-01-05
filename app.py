# app.py
# Copyright (C) 2025 Nicola Continisio
# Contact: mail@continisio.it
# More information: https://continisio.it
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import asyncio
import re
import json
from tqdm import tqdm
from telethon import TelegramClient, errors
from telethon.tl.types import MessageMediaDocument
from telethon.tl.functions.messages import ImportChatInviteRequest
import os

# Leggi i parametri di configurazione dal file config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

API_ID = config['API_ID']
API_HASH = config['API_HASH']
SESSION_NAME = config['SESSION_NAME']
PATH_DOWNLOAD = config.get('PATH_DOWNLOAD', '.')  # Cartella di download predefinita
LOG_FILE = os.path.join(PATH_DOWNLOAD, 'log.txt')

def validate_input(link):
    """Validazione del link o identificativo del canale."""
    patterns = [
        r'^https:\/\/t\.me\/\+\w+$',          # Link diretto con "+"
        r'^https:\/\/t\.me\/joinchat\/\w+$',  # Link di invito con "joinchat"
        r'^https:\/\/t\.me\/\w+$',            # Link generico per canali
        r'^https:\/\/web\.telegram\.org\/k\/\#-?\d+$',  # Link web Telegram con ID numerico
        r'^@\w+$',                               # Username del canale o gruppo
        r'^-?\d+$'                               # ID numerico
    ]
    for pattern in patterns:
        if re.match(pattern, link):
            return True
    return False

def clean_link(link):
    """Rimuove prefissi inutili per ottenere solo l'ID o hash necessario."""
    if link.startswith("https://web.telegram.org/k/#"):
        return link.split("#")[-1]
    if "joinchat" in link:
        return link.split("/")[-1]
    return link

async def fetch_messages(client, link):
    """Recupera i messaggi dal canale/gruppo Telegram e mantiene i nomi dei file originali."""
    messages = []
    try:
        print(f"Tentativo di recuperare l'entità da: {link}")

        # Gestione specifica per link joinchat
        if "joinchat" in link:
            try:
                entity = await client(ImportChatInviteRequest(link))
            except errors.InviteHashInvalidError:
                print("Errore: il link di invito non è valido.")
                return []
        else:
            # Per altri tipi di link o ID
            entity = await client.get_entity(link)

        print(f"Entità trovata: {entity}")

        async for message in client.iter_messages(entity):
            # Determina il nome del file
            file_name = None

            # Se c'è un file allegato, usa il nome originale o genera un nome unico
            if message.media and isinstance(message.media, MessageMediaDocument):
                file_name = message.file.name or f"document_{message.media.document.id}.mp4"

            messages.append({
                "id": message.id,
                "text": message.text or "No text",
                "media": file_name
            })

            # Mostra il messaggio durante il recupero
            print(f"{message.id}: {message.text or 'No text'} ({file_name})")

    except errors.FloodWaitError as e:
        print(f"Flood control attivo, riprovo tra {e.seconds} secondi...")
        await asyncio.sleep(e.seconds)
    except errors.ChannelInvalidError:
        print("Errore: link non valido o scaduto.")
    except errors.ChannelPrivateError:
        print("Errore: il canale è privato e non accessibile tramite API.")
    except ValueError as e:
        print(f"Errore durante il recupero dell'entità: {e}")
    except Exception as e:
        print(f"Errore generico: {e}")
    return messages

async def download_media(client, link, message_ids):
    """Scarica i media selezionati."""
    os.makedirs(PATH_DOWNLOAD, exist_ok=True)  # Assicura che la cartella di download esista

    with open(LOG_FILE, 'w') as log_file:
        for msg_id in message_ids:
            try:
                message = await client.get_messages(link, ids=msg_id)
                if message.media and isinstance(message.media, MessageMediaDocument):
                    # Usa sempre il nome originale del file
                    file_name = message.file.name or f"document_{message.media.document.id}.mp4"
                    file_size = message.file.size or 0
                    file_path = os.path.join(PATH_DOWNLOAD, file_name)

                    print(f"Scaricando {file_name} in {PATH_DOWNLOAD}...")

                    with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, desc=file_name) as pbar:
                        def progress_callback(current, total):
                            pbar.update(current - pbar.n)

                        await message.download_media(file=file_path, progress_callback=progress_callback)
                else:
                    print(f"Il messaggio {msg_id} non contiene media scaricabili.")
            except OSError as e:
                error_message = f"Errore: {e}"
                print(error_message)
                log_file.write(error_message + "\n")
            except errors.FloodWaitError as e:
                error_message = f"Flood control attivo! Attendo {e.seconds} secondi prima di riprendere il download del messaggio {msg_id}."
                print(error_message)
                log_file.write(error_message + "\n")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                error_message = f"Errore durante il download del messaggio {msg_id}: {e}"
                print(error_message)
                log_file.write(error_message + "\n")

async def main():
    link = input("Inserisci il link o identificativo del canale/gruppo Telegram: ").strip()
    link = clean_link(link)

    if not validate_input(link):
        print("Link o identificativo non valido.")
        return

    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        print("Client Telegram avviato.")
        print(f"Inizio elaborazione link: {link}")

        messages = await fetch_messages(client, link)

        if not messages:
            print("Nessun messaggio trovato.")
            return

        # Mostra la lista dei messaggi all'utente
        for i, msg in enumerate(messages, 1):  # i è l'indice visibile, msg contiene i dettagli
            print(f"{i}: {msg['text']} ({msg['media']})")

        while True:
            selection = input("Inserisci il numero del messaggio, intervalli o una serie di intervalli (es. 10,15,18-30), 'T' per tutti, 'Q' per uscire: ").strip()

            if selection.lower() == 'q':
                print("Uscita dal programma.")
                return

            if selection.lower() == 't':
                message_ids = [msg['id'] for msg in messages]
                break

            try:
                ranges = selection.split(',')
                selected_indices = []
                for r in ranges:
                    if '-' in r:
                        start, end = map(int, r.split('-'))
                        selected_indices.extend(range(start, end + 1))
                    else:
                        selected_indices.append(int(r))

                # Converti gli indici selezionati negli ID effettivi dei messaggi
                message_ids = [messages[i - 1]['id'] for i in selected_indices if 1 <= i <= len(messages)]
                break
            except (ValueError, IndexError):
                print("Errore: selezione non valida. Riprova.")

        await download_media(client, link, message_ids)

if __name__ == "__main__":
    asyncio.run(main())

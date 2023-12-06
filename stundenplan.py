import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import subprocess
from tkinter import Tk, Button, Toplevel, PhotoImage, Canvas
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import time

def download_and_open_pdf(last_modified_times):
    url = 'https://service.viona24.com/stpusnl/'  # URL

    response = requests.get(url)  # Anfrage senden, HTML-Inhalt erhalten
    response.encoding = 'utf-8'  # Korrekte Zeichenkodierung angeben
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')  # Mit BeautifulSoup HTML analysieren

    os.makedirs('downloaded_files', exist_ok=True)  # Verzeichnis erstellen

    links = [link for link in soup.find_all('a', href=True) if '.pdf' in link['href'] and '2023' in link.text and 'Winter' in link.text and 'FIAE D' in link.text]  # Abfrage-Bedingung

    for link in links:
        file_url = urljoin(url, link['href'])  # Falls die URL relativ ist, die absolute URL erstellen

        try:
            response = requests.head(file_url)
            last_modified = response.headers['Last-Modified']

            if file_url not in last_modified_times or last_modified_times[file_url] != last_modified:
                last_modified_times[file_url] = last_modified

                file_data = requests.get(file_url, verify=True, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, stream=True, allow_redirects=True).content  # Datei herunterladen

                file_filename = os.path.join('downloaded_files', os.path.basename(file_url))  # Dateipfad extrahieren

                with open(file_filename, 'wb') as file:  # Datei speichern
                    file.write(file_data)

                print(f'Datei erfolgreich heruntergeladen: {file_filename}')

                # PDF-Datei öffnen
                open_pdf_in_window(file_filename)

        except Exception as e:
            print(f"Fehler beim Herunterladen von {file_url}: {e}")

    print('Vergleiche und Öffne abgeschlossen.')

def open_pdf_in_window(pdf_filename):
    images = convert_from_path(pdf_filename)

    # Neues Fenster für PDF erstellen
    pdf_window = Toplevel()
    pdf_window.title('Stundenplan')

    # Canvas für Bilder erstellen
    canvas = Canvas(pdf_window, width=images[0].width, height=images[0].height)
    canvas.pack()

    for idx, img in enumerate(images):
        img_tk = ImageTk.PhotoImage(img)

        # Bild zum Canvas hinzufügen
        canvas.create_image(0, 0, anchor='nw', image=img_tk)

    pdf_window.mainloop()

# GUI erstellen
root = Tk()
root.title('PDF Downloader')
root.geometry('400x200')  # Fenstergröße festlegen

# Button zum manuellen Herunterladen und Öffnen von PDFs hinzufügen
download_button = Button(root, text='PDFs herunterladen und öffnen', command=lambda: download_and_open_pdf({}))
download_button.pack(pady=10)

# Button zum Beenden hinzufügen
exit_button = Button(root, text='Beenden', command=root.destroy)
exit_button.pack(pady=10)

# Tkinter-Fenster ausführen
root.mainloop()



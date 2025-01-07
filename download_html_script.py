import requests


def scarica_html(url):
    try:
        # Effettua una richiesta GET alla URL indicata
        risposta = requests.get(url)

        # Controlla che la richiesta sia andata a buon fine (status code 200)
        if risposta.status_code == 200:
            # Estrae il contenuto HTML come stringa
            codice_html = risposta.text
            return codice_html
        else:
            print(f"Errore nella richiesta: codice di stato {risposta.status_code}")
            return None
    except Exception as e:
        print(f"Errore durante il download dell'HTML: {e}")
        return None


# URL del file HTML
url_file_html = "http://35.205.92.199:8093/files/685675637467/bilancio_sostenibilita.html"

# Scarica e stampa il contenuto HTML
codice_html = scarica_html(url_file_html)
if codice_html:
    print("Codice HTML scaricato con successo:")
    print(codice_html)

import requests
from bs4 import BeautifulSoup
import json
import os
import re

USER = "Shadorossa"
URL = f"https://backloggd.com/u/{USER}/games/"
# Ruta donde guardaremos el JSON
OUTPUT_PATH = "data/games.json"
LOCAL_COVERS_DIR = "img/covers/"

def slugify(text):
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def fetch_backloggd():
    print(f"--- Iniciando scraping de Backloggd para {USER} ---")
    
    # Cabeceras para que la web crea que somos un navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print(f"Error: No se pudo acceder a Backloggd (Status: {response.status_code})")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscamos los contenedores de los juegos
    # En Backloggd, suelen estar dentro de 'col-xl-2' o clases similares de grid
    game_cards = soup.find_all('div', class_='game-card-cl')
    
    results = []
    for card in game_cards:
        # Extraer Título
        title_tag = card.find('div', class_='game-title')
        title = title_tag.text.strip() if title_tag else "Sin título"
        
        # Extraer Imagen
        img_tag = card.find('img', class_='game-cover')
        img_url = img_tag['src'] if img_tag else ""

        # Lógica de Imagen Local
        local_filename = f"{slugify(title)}.jpg"
        local_path = os.path.join(LOCAL_COVERS_DIR, local_filename)
        # Comprobamos si el archivo existe físicamente en la carpeta
        final_image = local_path if os.path.exists(local_path) else img_url

        # Solo guardamos si el juego tiene título
        if title != "Sin título":
            results.append({
                "title": title,
                "image": final_image,
                "type": "game",
                "score": None # Backloggd no muestra la nota en la lista general fácilmente
            })

    # Guardar resultados
    os.makedirs('data', exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Éxito: Se han encontrado {len(results)} juegos.")

if __name__ == "__main__":
    fetch_backloggd()
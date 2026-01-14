import requests
from bs4 import BeautifulSoup
import json
import os
import re

# Configuración
USER = "Shadorossa"
URL = f"https://backloggd.com/u/{USER}/games/"
LOCAL_COVERS_DIR = "img/covers/"

def slugify(text):
    # Convierte "The Legend of Zelda" en "the_legend_of_zelda" para buscar el archivo
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def get_backloggd_games():
    print(f"Buscando juegos de {USER} en Backloggd...")
    response = requests.get(URL)
    if response.status_code != 200:
        print("Error al acceder a Backloggd")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    games_data = []

    # Buscamos cada contenedor de juego
    # Nota: Los selectores pueden cambiar si la web se actualiza
    game_elements = soup.select('.game-card-cl') 

    for element in game_elements:
        title = element.select_one('.game-title').text.strip() if element.select_one('.game-title') else "Unknown"
        img_url = element.select_one('img')['src'] if element.select_one('img') else ""
        
        # Lógica de puntuación (Backloggd usa estrellas o texto)
        score_element = element.select_one('.stars-text')
        score = score_element.text.strip() if score_element else None

        # --- LÓGICA DE IMAGEN LOCAL ---
        filename = f"{slugify(title)}.jpg"
        local_path = os.path.join(LOCAL_COVERS_DIR, filename)
        
        # Si existe el archivo físico en tu repo, usamos esa ruta
        final_image = local_path if os.path.exists(local_path) else img_url

        games_data.append({
            "title": title,
            "image": final_image,
            "score": score,
            "status": "Completed"
        })

    return games_data

# Guardar en data/games.json
if __name__ == "__main__":
    games = get_backloggd_games()
    os.makedirs('data', exist_ok=True)
    with open('data/games.json', 'w', encoding='utf-8') as f:
        json.dump(games, f, ensure_ascii=False, indent=4)
    print(f"Finalizado. Se han encontrado {len(games)} juegos.")
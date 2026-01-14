import requests
from bs4 import BeautifulSoup
import json
import os

USER = "Shadorossa"
URL = f"https://backloggd.com/u/{USER}/games/"

def fetch_games():
    print(f"Sincronizando Backloggd para {USER}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    game_cards = soup.find_all('div', class_='game-card-cl')
    
    results = []
    for card in game_cards:
        title = card.find('div', class_='game-title').text.strip()
        img_url = card.find('img', class_='game-cover')['src']
        
        # Comprobar imagen local
        local_name = title.lower().replace(" ", "_").replace(":", "") + ".jpg"
        local_path = f"img/covers/{local_name}"
        final_img = local_path if os.path.exists(local_path) else img_url
        
        results.append({"title": title, "image": final_img, "type": "game"})

    os.makedirs('data', exist_ok=True)
    json.dump(results, open('data/games.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

if __name__ == "__main__":
    fetch_games()
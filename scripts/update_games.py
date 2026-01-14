import asyncio
import json
import re
import inspect
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# --- REPARACIÓN QUIRÚRGICA DE IMPORTACIÓN ---
try:
    import playwright_stealth
    # Buscamos la función 'stealth' o 'Stealth' dentro del módulo
    if hasattr(playwright_stealth, 'stealth'):
        stealth_func = playwright_stealth.stealth
    elif hasattr(playwright_stealth, 'Stealth'):
        stealth_func = playwright_stealth.Stealth
    else:
        # Intento de importación profunda desde el archivo stealth.py
        from playwright_stealth.stealth import Stealth as stealth_func
except (ImportError, AttributeError):
    # Último recurso: importación directa
    from playwright_stealth.stealth import Stealth as stealth_func

# --- CONFIGURACIÓN ---
USERNAME = 'TuUsuarioDeBackloggd'  # <--- CAMBIA ESTO
BASE_URL = f"https://www.backloggd.com/u/{USERNAME}/games/release?type=played"

async def fetch_games():
    async with async_playwright() as p:
        print(f"Iniciando navegador ultra-stealth para: {USERNAME}...")
        
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        # Ejecutamos la función de sigilo detectada
        if inspect.iscoroutinefunction(stealth_func):
            await stealth_func(page)
        else:
            stealth_func(page)
        
        try:
            print(f"Navegando a {BASE_URL}...")
            await page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(6) # Tiempo para Cloudflare
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            game_cards = soup.select('.game-cover-wrapper')
            print(f"Analizando {len(game_cards)} posibles juegos encontrados...")
            
            games_data = []
            for card in game_cards:
                img_tag = card.find('img')
                title = img_tag['alt'] if img_tag else "Unknown"
                img_url = img_tag['src'] if img_tag else ""
                link_tag = card.find_parent('a')
                full_url = f"https://www.backloggd.com{link_tag['href']}" if link_tag else "#"

                # Nota calculada por ancho de estrellas
                score = 0
                star_div = card.select_one('.stars-top')
                if star_div and 'style' in star_div.attrs:
                    match = re.search(r'width:\s*(\d+)%', star_div['style'])
                    if match:
                        score = round(int(match.group(1)) / 10, 1)

                games_data.append({
                    "title": title, "image": img_url, "type": "game",
                    "score": score, "url": full_url, "finishDate": "2026-01-01" 
                })

            if games_data:
                print(f"Éxito: {len(games_data)} juegos guardados en data/games.json")
                with open('data/games.json', 'w', encoding='utf-8') as f:
                    json.dump(games_data, f, indent=4, ensure_ascii=False)
            else:
                print("Error: El navegador no detectó juegos.")

        except Exception as e:
            print(f"Error crítico: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_games())
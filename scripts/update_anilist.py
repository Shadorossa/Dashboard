import requests
import json
import os

USER = "Shadorossa"
URL = 'https://graphql.anilist.co'

def format_date(date_obj):
    if not date_obj or not date_obj.get('year'):
        return "0000-00-00"
    y = date_obj.get('year')
    m = date_obj.get('month') or 1
    d = date_obj.get('day') or 1
    return f"{y}-{m:02d}-{d:02d}"

def fetch_anilist(media_type):
    print(f"Sincronizando {media_type} con notas...")
    query = '''
    query ($username: String, $type: MediaType) {
      MediaListCollection(userName: $username, type: $type, status: COMPLETED) {
        lists { 
          entries { 
            score(format: POINT_10)
            completedAt { year month day }
            media { 
              title { romaji } 
              coverImage { large } 
              siteUrl # <--- AÑADE ESTO
            } 
          } 
        }
      }
    }
    '''

    variables = {'username': USER, 'type': media_type.upper()}
    try:
        response = requests.post(URL, json={'query': query, 'variables': variables})
        data = response.json()
        results = []
        seen = set()
        for collection in data['data']['MediaListCollection']['lists']:
            for entry in collection['entries']:
                title = entry['media']['title']['romaji']
                if title not in seen:
                    results.append({
                        "title": title,
                        "image": entry['media']['coverImage']['large'],
                        "type": media_type.lower(),
                        "score": entry['score'] if entry['score'] > 0 else 0,
                        "url": entry['media']['siteUrl'],
                        "finishDate": format_date(entry['completedAt'])
                    })
                    seen.add(title)
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    json.dump(fetch_anilist("ANIME"), open('data/anime.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
    json.dump(fetch_anilist("MANGA"), open('data/manga.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
    print("Transporte de AniList (con notas) finalizado.")
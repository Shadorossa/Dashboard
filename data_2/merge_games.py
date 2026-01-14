import json
import glob
import os
from datetime import datetime

def normalize_date_manual(date_str):
    """
    Transforma 'Jan 1 2026' o 'jan 1 2026' en '2026-01-01'
    usando mapeo manual para evitar errores de idioma.
    """
    if not date_str or not isinstance(date_str, str) or date_str.strip() == "":
        return "", datetime.min

    # Diccionario de meses para asegurar conversión
    months = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }

    parts = date_str.strip().lower().split()

    if len(parts) == 3:
        try:
            mes_texto = parts[0][:3] # Toma las primeras 3 letras
            mes_num = months.get(mes_texto, '01')
            dia = parts[1].zfill(2) # '1' -> '01'
            anio = parts[2]
            
            iso_date = f"{anio}-{mes_num}-{dia}"
            dt_obj = datetime.strptime(iso_date, "%Y-%m-%d")
            return iso_date, dt_obj
        except Exception:
            return date_str, datetime.min
    
    # Si ya está en formato YYYY-MM-DD
    try:
        dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_str, dt_obj
    except:
        return date_str, datetime.min

def unificar_archivos():
    # 1. Localizar archivos en la carpeta del script (data_2)
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    patron = os.path.join(directorio_actual, "games*.json")
    archivos = glob.glob(patron)
    
    if not archivos:
        print(f"Error: No se encontraron archivos 'games*.json' en: {directorio_actual}")
        return

    lista_maestra = []
    
    # 2. Cargar todos los archivos
    for ruta in archivos:
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    lista_maestra.extend(data)
                    print(f"✔ Cargado: {os.path.basename(ruta)}")
        except Exception as e:
            print(f"✘ Error en {os.path.basename(ruta)}: {e}")

    # 3. Normalizar y eliminar duplicados
    dict_unicos = {}
    for juego in lista_maestra:
        url = juego.get('url')
        if not url: continue
        
        # PROCESO DE FECHA ISO
        raw_date = juego.get('finishDate', '')
        fixed_date_str, dt_obj = normalize_date_manual(raw_date)
        juego['finishDate'] = fixed_date_str
        juego['_dt_sort'] = dt_obj

        if url not in dict_unicos:
            dict_unicos[url] = juego
        else:
            # Si el juego ya existe, priorizamos el que tenga fecha válida
            if dict_unicos[url]['_dt_sort'] == datetime.min and dt_obj > datetime.min:
                dict_unicos[url] = juego

    # 4. Ordenar (Recientes primero)
    resultado = list(dict_unicos.values())
    resultado.sort(key=lambda x: x['_dt_sort'], reverse=True)

    # Limpiar basura técnica
    for j in resultado:
        j.pop('_dt_sort', None)

    # 5. Guardar en la carpeta data/ principal
    ruta_proyecto = os.path.dirname(directorio_actual)
    ruta_data = os.path.join(ruta_proyecto, "data")
    os.makedirs(ruta_data, exist_ok=True)
    
    ruta_final = os.path.join(ruta_data, "games.json")

    with open(ruta_final, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)

    print("-" * 30)
    print(f"ÉXITO: {len(resultado)} juegos unificados.")
    print(f"FECHA FIJADA: YYYY-MM-DD")
    print(f"DESTINO: {ruta_final}")

if __name__ == "__main__":
    unificar_archivos()
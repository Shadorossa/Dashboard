import json
import glob
import os
from datetime import datetime

def normalize_date(date_str):
    """
    Transforma formatos como 'Oct 19 2024' o 'oct 19 2024' 
    en el estándar '2024-10-19' (Año-Mes-Día).
    """
    if not date_str or not isinstance(date_str, str) or date_str.strip() == "":
        return "", datetime.min
    
    parts = date_str.strip().split()
    # Esperamos 3 partes: Mes, Día, Año
    if len(parts) == 3:
        try:
            # Normalizar el mes (primera mayúscula)
            month = parts[0].capitalize()
            day = parts[1]
            year = parts[2]
            
            # Formato de entrada: 'Oct 19 2024'
            input_str = f"{month} {day} {year}"
            dt = datetime.strptime(input_str, "%b %d %Y")
            
            # Formato de salida: '2024-10-19'
            iso_date = dt.strftime("%Y-%m-%d")
            return iso_date, dt
        except Exception:
            # Si falla el parseo, devolvemos la cadena original para no perder datos
            return date_str, datetime.min
    else:
        # Si ya está en formato YYYY-MM-DD o es desconocido
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return date_str, dt
        except:
            return date_str, datetime.min

def unificar_archivos():
    # 1. Detectar directorio donde se encuentra el script
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    patron = os.path.join(directorio_actual, "games*.json")
    archivos = glob.glob(patron)
    
    if not archivos:
        print(f"Error: No se encontraron archivos 'games*.json' en: {directorio_actual}")
        return

    lista_maestra = []
    
    # 2. Cargar datos de todos los archivos encontrados
    for ruta_archivo in archivos:
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    lista_maestra.extend(data)
                    print(f"✔ Cargados {len(data)} juegos de {os.path.basename(ruta_archivo)}")
        except Exception as e:
            print(f"✘ Error al leer {os.path.basename(ruta_archivo)}: {e}")

    # 3. Procesar fechas y eliminar duplicados por URL
    dict_unicos = {}
    for juego in lista_maestra:
        url = juego.get('url')
        if not url: continue
        
        # Aplicar el nuevo formato Año-Mes-Día
        raw_date = juego.get('finishDate', '')
        fixed_date_str, dt_obj = normalize_date(raw_date)
        juego['finishDate'] = fixed_date_str
        juego['_dt_sort'] = dt_obj # Atributo auxiliar para ordenar

        if url not in dict_unicos:
            dict_unicos[url] = juego
        else:
            # Si el juego está repetido, priorizamos la entrada que tenga fecha válida
            if dict_unicos[url]['_dt_sort'] == datetime.min and dt_obj > datetime.min:
                dict_unicos[url] = juego

    # 4. Ordenar cronológicamente (más recientes primero)
    resultado_final = list(dict_unicos.values())
    resultado_final.sort(key=lambda x: x['_dt_sort'], reverse=True)

    # Eliminar el atributo auxiliar antes de guardar
    for j in resultado_final:
        j.pop('_dt_sort', None)

    # 5. Guardar el resultado en Dashboard/data/games.json
    ruta_proyecto = os.path.dirname(directorio_actual)
    ruta_salida_carpeta = os.path.join(ruta_proyecto, "data")
    ruta_salida_archivo = os.path.join(ruta_salida_carpeta, "games.json")

    os.makedirs(ruta_salida_carpeta, exist_ok=True)

    with open(ruta_salida_archivo, 'w', encoding='utf-8') as f:
        json.dump(resultado_final, f, indent=4, ensure_ascii=False)

    print("-" * 40)
    print(f"PROCESO TERMINADO")
    print(f"Juegos únicos finales: {len(resultado_final)}")
    print(f"Formato aplicado: Año-Mes-Día (YYYY-MM-DD)")
    print(f"Archivo guardado en: {ruta_salida_archivo}")

if __name__ == "__main__":
    unificar_archivos()
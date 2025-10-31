# generarPaises.py

import requests
import csv
import os

def obtener_y_guardar_paises(url, nombre_archivo, carpeta_salida):
    """
    Obtiene datos de la API y los guarda en un CSV dentro de una carpeta específica.
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f"Carpeta '{carpeta_salida}' creada exitosamente.")

    ruta_completa_archivo = os.path.join(carpeta_salida, nombre_archivo)
    
    print(f"Obteniendo datos desde {url}...")
    
    try:
        response = requests.get(url) 
        response.raise_for_status()
        
        paises = response.json()
        print(f"Se encontraron {len(paises)} territorios. Procesando...")

        with open(ruta_completa_archivo, 'w', newline='', encoding='utf-8') as archivo_csv:
            campos = ['nombre_comun_es', 'nombre_oficial_es', 'capital', 'region', 'poblacion', 'area']
            escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
            escritor.writeheader()
            
            for pais in paises:
                escritor.writerow({
                    'nombre_comun_es': pais.get('translations', {}).get('spa', {}).get('common', 'N/A'),
                    'nombre_oficial_es': pais.get('translations', {}).get('spa', {}).get('official', 'N/A'),
                    'capital': ', '.join(pais.get('capital', ['N/A'])),
                    'region': pais.get('region', 'N/A'),
                    'poblacion': pais.get('population', 0),
                    'area': int(pais.get('area', 0.0))
                })
        print(f"¡Éxito! Los datos han sido guardados en el archivo '{ruta_completa_archivo}'.")
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# Nueva Función Añadida
def unir_csvs_en_uno(carpeta_entrada, archivo_salida):
    """
    Busca todos los archivos .csv en una carpeta, les añade una columna 'continente',
    y los une en un único archivo.
    """
    nombre_archivo_salida = os.path.basename(archivo_salida)
    archivos_csv_a_unir = [
        f for f in os.listdir(carpeta_entrada)
        if f.endswith('.csv') and f != nombre_archivo_salida
    ]

    if not archivos_csv_a_unir:
        print("No se encontraron archivos de continentes para unir.")
        return

    print(f"\nUniendo {len(archivos_csv_a_unir)} archivos en '{archivo_salida}'...")
    
    with open(archivo_salida, 'w', newline='', encoding='utf-8') as f_salida:
        escritor = csv.writer(f_salida)
        
        # Leemos el primer archivo para obtener la cabecera
        primer_archivo = os.path.join(carpeta_entrada, archivos_csv_a_unir[0])
        with open(primer_archivo, 'r', encoding='utf-8') as f_entrada:
            lector = csv.reader(f_entrada)
            cabecera = next(lector)
            
            # Añadimos la Nueva Columna a la Cabecera
            cabecera.append('continente')
            escritor.writerow(cabecera)
        
        # Recorremos todos los archivos CSV para añadir su contenido
        for nombre_archivo in archivos_csv_a_unir:
            print(f"  - Procesando y añadiendo: {nombre_archivo}")
            # Extraemos el nombre del continente del nombre del archivo
            continente = nombre_archivo.replace('.csv', '')
            
            ruta_completa = os.path.join(carpeta_entrada, nombre_archivo)
            with open(ruta_completa, 'r', encoding='utf-8') as f_entrada:
                lector = csv.reader(f_entrada)
                next(lector) # Saltamos la Cabecera de este Archivo
                for fila in lector:
                    # Añadimos el Nombre del Continente a Cada Fila
                    fila.append(continente)
                    escritor.writerow(fila)
                    
    print(f"¡Éxito! Archivo '{archivo_salida}' creado correctamente con la columna 'continente'.")
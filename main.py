# main.py
import os
import interfaz
# Importa AMBAS funciones del archivo 'generarPaises.py'
from generarPaises import obtener_y_guardar_paises, unir_csvs_en_uno

def procesar_todos_los_continentes():
    # Esta función no cambia
    continentes = ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania', 'Antarctic']
    carpeta_salida = "Continentes"
    print("--- INICIANDO PROCESO DE DESCARGA DE DATOS ---")
    for continente in continentes:
        print(f"\nProcesando {continente}...")
        url = f"https://restcountries.com/v3.1/region/{continente}"
        nombre_archivo = f"{continente}.csv"
        obtener_y_guardar_paises(url, nombre_archivo, carpeta_salida)
    print("\n--- ¡PROCESO DE DESCARGA COMPLETADO! ---")

if __name__ == "__main__":
    
    # Genera los CSVs individuales para cada continente.
    procesar_todos_los_continentes()
    
    # Llama a la nueva función para unirlos todos.
    carpeta_continentes = "Continentes"
    nombre_archivo_final = "Todos.csv"
    
    # Línea Corregida
    # Unimos la carpeta y el nombre para crear la ruta completa.
    ruta_archivo_final = os.path.join(carpeta_continentes, nombre_archivo_final)
    
    # Le pasamos la ruta completa a la función.
    unir_csvs_en_uno(carpeta_continentes, ruta_archivo_final)

    # Iniciamos la Interfaz
    interfaz.iniciar_interfaz()
# interfaz.py
#Este módulo se encarga de crear la Interfaz Gráfica de Usuario (GUI)
# y gestionar la visualización, búsqueda, ordenamiento y filtrado de los datos de países.

import tkinter as tk # Importa la biblioteca principal de Tkinter.
from tkinter import ttk, messagebox # Importa widgets temáticos (ttk) y cuadros de diálogo.
import csv # Importa el módulo para leer archivos CSV.
import os # Importa el módulo para interactuar con el sistema operativo (e.g., rutas de archivos).
from collections import Counter # Importa la clase Counter para realizar conteos (usada en estadísticas).

# Variables Globales
# Estas variables son accesibles y modificables desde cualquier función.
dataset_paises = [] # Lista principal que almacena todos los datos de los países cargados del CSV
texto_busqueda_var = None # Variable de control para el campo de búsqueda rápida.
tree = None # Referencia al widget de tabla (Treeview) para manipular su contenido.
ventana = None # Referencia a la ventana principal de la aplicación.
combo_ordenar = None # Referencia al menú desplegable para ordenar.

# Funciones de Datos y Lógica
#Carga los datos del archivo CSV en la variable global 'dataset_paises'.
#Cada país se almacena como un diccionario.
def cargar_datos_en_memoria(archivo_csv):
    dataset = [] # Inicializa una lista vacía para los datos.
    try: # Inicia el bloque de manejo de excepciones.
        if not os.path.exists(archivo_csv): # Verifica si el archivo existe.
            # Lanza un error si el archivo no existe.
            raise FileNotFoundError
        with open(archivo_csv, mode='r', encoding='utf-8') as archivo: # Abre el archivo.
            # El DictReader lee cada fila como un diccionario, usando la cabecera como claves.
            lector_csv = csv.DictReader(archivo) # Crea un lector que trata las filas como diccionarios.
            for fila in lector_csv: # Itera sobre cada fila del CSV.
                # Intenta convertir a número los campos 'poblacion' y 'area'
                dataset.append(fila) # Agrega la fila (diccionario de país) a la lista.
        return dataset # Devuelve la lista cargada.
    except FileNotFoundError: # Captura si el archivo no existe.
        messagebox.showerror("Error", f"No se encontró el archivo de datos:\n{archivo_csv}") # Muestra un error.
        return None
    except Exception as e: # Captura cualquier otro error de lectura.
        messagebox.showerror("Error", f"Ocurrió un error al leer el archivo: {e}")
        return None

def mostrar_datos_en_treeview(tree, dataset, columnas):
    """Limpia el Treeview y lo llena con los datos del dataset filtrado/ordenado."""
    tree.delete(*tree.get_children()) # Borra todas las filas del Treeview.
    if not dataset: # Si el dataset está vacío,
        return # sale de la función.
    for fila_dict in dataset: # Itera sobre los países del dataset.
        valores = [fila_dict.get(col, '') for col in columnas] # Prepara la lista de valores para la fila.
        tree.insert("", "end", values=valores) # Inserta la nueva fila en la tabla.

# Función de Ordenamiento
def ordenar_desde_controles(es_descendente):
    """
    Función para ordenar activada por los botones de la interfaz.
    Recibe True para orden descendente, False para ascendente.
    """
    global dataset_paises, combo_ordenar, tree
    
    mapa_columnas = {"Nombre": "nombre_comun_es", "Población": "poblacion", "Superficie": "area", "Continente": "continente"} # Mapeo de nombres visibles a claves internas.
    opcion_elegida = combo_ordenar.get() # Obtiene la columna seleccionada para ordenar.
    
    if not opcion_elegida: # Verifica que se haya seleccionado una opción.
        messagebox.showwarning("Aviso", "Por favor, selecciona un criterio para ordenar.")
        return
        
    columna_a_ordenar = mapa_columnas[opcion_elegida] # Obtiene la clave interna para ordenar.
    columnas_visibles = list(mapa_columnas.values()) # Obtiene la lista de claves para mostrar.
    
    # 1. Función Clave para Ordenar (maneja números y texto)
    def clave_orden(item): # Función para determinar cómo se comparan los elementos.
        valor = item.get(columna_a_ordenar, '')
        try: # Intenta convertir a número (para ordenar por valor numérico).
            return float(valor)
        except (ValueError, TypeError): # Si no es numérico, lo trata como texto.
            return str(valor).lower()
            
    # 2. Ordena el dataset_paises Global
    dataset_paises.sort(key=clave_orden, reverse=es_descendente) # Ordena el dataset usando la clave y la dirección (asc/desc).
    
    # 3. Actualiza la Vista (Treeview)
    if texto_busqueda_var and texto_busqueda_var.get(): # Verifica si hay un filtro de búsqueda aplicado.
          # Si hay texto de búsqueda, aplicamos el filtro de nuevo para mostrar el resultado ordenado
          buscar_pais(tree, dataset_paises, columnas_visibles, texto_busqueda_var) # Si hay búsqueda, la aplica al dataset ordenado.
    else:
          # Si no hay texto de búsqueda, mostramos todo el dataset ordenado
          mostrar_datos_en_treeview(tree, dataset_paises, columnas_visibles) # Si no hay búsqueda, muestra todo el dataset ordenado.

# Función de Búsqueda
def buscar_pais(tree, dataset, columnas_visibles, texto_busqueda_var):
    #Filtra el dataset de países y actualiza el Treeview
    #para mostrar solo aquellos cuyo nombre comienza con el texto buscado.
 
    texto_busqueda = texto_busqueda_var.get().strip().lower() # Obtiene el texto de búsqueda y lo normaliza.

    if not texto_busqueda: # Si la búsqueda está vacía,
        # Si la búsqueda está vacía, muestra todos los datos
        mostrar_datos_en_treeview(tree, dataset, columnas_visibles) # Muestra todo el dataset.
        return

    # Filtra los Países
    resultados = [ # Filtra los países.
        pais for pais in dataset 
        if pais.get('nombre_comun_es', '').lower().startswith(texto_busqueda) # Compara si el nombre empieza por el texto buscado.
    ]

    if not resultados and texto_busqueda: # Si no hay resultados y la búsqueda no está vacía.
        messagebox.showinfo("Búsqueda", f"No se encontraron países que comiencen con '{texto_busqueda}'.")
    
    # Muestra los resultados en el Treeview
    mostrar_datos_en_treeview(tree, resultados, columnas_visibles) # Muestra los resultados en la tabla.

# Función de Filtrado
def aplicar_filtro(tree, dataset, columnas_visibles, ventana_filtro,
                   continente_var, min_pob_var, max_pob_var, min_area_var, max_area_var): # Función que aplica los criterios de filtrado.
    """
    Filtra el dataset de países basándose en los criterios de Continente, Población y Superficie.
    """
    try:
        # 1. Obtener y Validar Valores de Entrada
        continente_elegido = continente_var.get()
        
        # Eliminamos puntos y convertimos a entero/float
        min_pob = int(min_pob_var.get().replace('.', '')) if min_pob_var.get() else None # Obtiene y convierte la población mínima.
        max_pob = int(max_pob_var.get().replace('.', '')) if max_pob_var.get() else None # Obtiene y convierte la población máxima.
        
        min_area = float(min_area_var.get().replace('.', '')) if min_area_var.get() else None # Obtiene y convierte el área mínima.
        max_area = float(max_area_var.get().replace('.', '')) if max_area_var.get() else None # Obtiene y convierte el área máxima.

        # 2. Aplicar el Filtro
        resultados = []
        for pais in dataset: # Itera sobre cada país.
            cumple_filtro = True # Bandera para el cumplimiento de criterios.
            
            # 1: Continente
            if continente_elegido and continente_elegido != "Todos" and pais.get('continente') != continente_elegido: # Comprueba el continente.
                cumple_filtro = False
            
            # 2: Rango de Población
            poblacion = int(pais.get('poblacion', 0))
            if cumple_filtro and min_pob is not None and poblacion < min_pob: # Comprueba población mínima.
                cumple_filtro = False
            if cumple_filtro and max_pob is not None and poblacion > max_pob: # Comprueba población máxima.
                cumple_filtro = False

            # 3: Rango de Superficie
            area = float(pais.get('area', 0.0)) 
            if cumple_filtro and min_area is not None and area < min_area: # Comprueba superficie mínima.
                cumple_filtro = False
            if cumple_filtro and max_area is not None and area > max_area: # Comprueba superficie máxima.
                cumple_filtro = False

            if cumple_filtro: # Si cumple todos los criterios.
                resultados.append(pais) # Añade el país a los resultados.

        # 3. Mostrar Resultados
        if not resultados:
            messagebox.showinfo("Filtro", "No se encontraron países que cumplan con todos los criterios de filtro.")
            mostrar_datos_en_treeview(tree, [], columnas_visibles) # Limpia la tabla si no hay resultados.
        else:
            mostrar_datos_en_treeview(tree, resultados, columnas_visibles) # Muestra los resultados filtrados.
        
        ventana_filtro.destroy() # Cierra la ventana de filtro al aplicar.

    except ValueError: # Captura errores si se introducen valores no numéricos.
        messagebox.showerror("Error de Entrada", "Por favor, introduce números válidos. Asegúrate de no usar comas como separador de miles.")
    except Exception as e: # Captura otros errores inesperados.
        messagebox.showerror("Error", f"Ocurrió un error inesperado al filtrar: {e}")

# Ventana de Filtrado
def mostrar_ventana_filtro():
    """Crea y muestra la ventana de diálogo para seleccionar los filtros."""
    global dataset_paises, ventana, tree 
    
    if not dataset_paises:
        messagebox.showinfo("Filtro", "No hay datos cargados para filtrar.")
        return

    # Obtener la Lista Única de Continentes
    continentes = sorted(list(set(p.get('continente') for p in dataset_paises if p.get('continente')))) # Extrae la lista de continentes únicos.
    opciones_continentes = ["Todos"] + continentes # Agrega la opción "Todos".
    
    # 1. Crear la Ventana de Diálogo (Toplevel)
    ventana_filtro = tk.Toplevel(ventana) # Crea una nueva ventana secundaria.
    ventana_filtro.title("Filtrar Países")
    ventana_filtro.geometry("400x350")
    ventana_filtro.resizable(False, False)
    
    frame_filtro = ttk.Frame(ventana_filtro, padding="15") # Crea un marco para organizar los controles.
    frame_filtro.pack(fill="both", expand=True)
    
    # Variables de Control
    continente_var = tk.StringVar(value="Todos") # Variable de control para el continente.
    min_pob_var = tk.StringVar()  # Variable de control para la población mínima.
    max_pob_var = tk.StringVar()
    min_area_var = tk.StringVar()
    max_area_var = tk.StringVar()

    row_count = 0
    
    # 1: Continente
    ttk.Label(frame_filtro, text="1. Continente:", font=("Helvetica", 10, "bold")).grid(row=row_count, column=0, sticky="w", pady=(10, 5))
    row_count += 1
    combo_continentes = ttk.Combobox(frame_filtro, textvariable=continente_var, values=opciones_continentes, state="readonly") # Combobox para seleccionar el continente.
    combo_continentes.grid(row=row_count, column=0, columnspan=2, sticky="ew", padx=5)
    row_count += 1

    # 2: Rango de Población
    ttk.Label(frame_filtro, text="2. Rango de Población: (Ej: 1000000)").grid(row=row_count, column=0, sticky="w", pady=(10, 5))
    row_count += 1
    
    ttk.Label(frame_filtro, text="Mínimo:").grid(row=row_count, column=0, sticky="w")
    ttk.Entry(frame_filtro, textvariable=min_pob_var, width=15).grid(row=row_count, column=1, sticky="w", padx=5) # Campo de entrada para población mínima.
    row_count += 1

    ttk.Label(frame_filtro, text="Máximo:").grid(row=row_count, column=0, sticky="w")
    ttk.Entry(frame_filtro, textvariable=max_pob_var, width=15).grid(row=row_count, column=1, sticky="w", padx=5) # Campo de entrada para población máxima.
    row_count += 1

    # 3: Rango de Superficie (Área)
    ttk.Label(frame_filtro, text="3. Rango de Superficie (km²):").grid(row=row_count, column=0, sticky="w", pady=(10, 5))
    row_count += 1
    
    ttk.Label(frame_filtro, text="Mínimo:").grid(row=row_count, column=0, sticky="w")
    ttk.Entry(frame_filtro, textvariable=min_area_var, width=15).grid(row=row_count, column=1, sticky="w", padx=5) # Campo de entrada para área mínima.
    row_count += 1

    ttk.Label(frame_filtro, text="Máximo:").grid(row=row_count, column=0, sticky="w")
    ttk.Entry(frame_filtro, textvariable=max_area_var, width=15).grid(row=row_count, column=1, sticky="w", padx=5) # Campo de entrada para área máxima.
    row_count += 1

    # Botón de Aplicar Filtro
    columnas_a_mostrar = {"nombre_comun_es": "Nombre", "poblacion": "Población", "area": "Superficie", "continente": "Continente"}
    nombres_internos_columnas = list(columnas_a_mostrar.keys())

    ttk.Button(frame_filtro, 
               text="Aplicar Filtro", 
               command=lambda: aplicar_filtro( # Botón que llama a aplicar_filtro con todas las variables de la GUI.
                   tree, dataset_paises, nombres_internos_columnas, ventana_filtro,
                   continente_var, min_pob_var, max_pob_var, min_area_var, max_area_var
               )
    ).grid(row=row_count, column=0, columnspan=2, sticky="ew", pady=(20, 5))
    
    frame_filtro.grid_columnconfigure(0, weight=1)
    frame_filtro.grid_columnconfigure(1, weight=1)

# Función para la Ventana de Estadística
def mostrar_ventana_estadisticas():
    """Calcula las estadísticas y las muestra en una nueva ventana."""
    global dataset_paises, ventana
    if not dataset_paises:
        messagebox.showinfo("Estadísticas", "No hay datos cargados para mostrar estadísticas.")
        return

    # 1. Realizar los Cálculos
    try:
        for pais in dataset_paises: # Itera y convierte los campos numéricos.
            pais['poblacion_num'] = float(pais.get('poblacion', 0)) if pais.get('poblacion') else 0
            pais['area_num'] = float(pais.get('area', 0.0)) if pais.get('area') else 0.0

        paises_con_datos = [p for p in dataset_paises if p['poblacion_num'] > 0 and p['area_num'] >= 0] # Filtra solo países con datos numéricos válidos.
        if not paises_con_datos:
            messagebox.showinfo("Estadísticas", "No hay países con datos numéricos válidos para calcular estadísticas.")
            return

        pais_max_pob = max(paises_con_datos, key=lambda p: p['poblacion_num']) # Encuentra el país con la población máxima.
        pais_min_pob = min(paises_con_datos, key=lambda p: p['poblacion_num']) # Encuentra el país con la población mínima.
        
        total_paises = len(paises_con_datos)
        promedio_poblacion = sum(p['poblacion_num'] for p in paises_con_datos) / total_paises # Calcula el promedio de población.
        promedio_superficie = sum(p['area_num'] for p in paises_con_datos) / total_paises # Calcula el promedio de superficie.
        
        conteo_continentes = Counter(p['continente'] for p in paises_con_datos) # Cuenta los países por continente.

    except (ValueError, TypeError) as e:
        messagebox.showerror("Error de Datos", f"No se pudieron calcular las estadísticas. Revisa los datos en el CSV.\nError: {e}")
        return

    # 2. Crear la Nueva ventana (Toplevel)
    ventana_stats = tk.Toplevel(ventana) # Crea la ventana de estadísticas.
    ventana_stats.title("Estadísticas Globales")
    ventana_stats.geometry("450x400")
    ventana_stats.resizable(False, False)

    frame_stats = ttk.Frame(ventana_stats, padding="10")
    frame_stats.pack(fill="both", expand=True)

    # 3. Mostrar los Resultados
    ttk.Label(frame_stats, text="Estadísticas de Países", font=("Helvetica", 14, "bold")).pack(pady=(0,10))
    
    frame_resultados = ttk.Frame(frame_stats)
    frame_resultados.pack(fill="x")

    def crear_linea_stat(parent, etiqueta, valor): # Función auxiliar para mostrar un par de etiqueta/valor en la estadística.
        ttk.Label(parent, text=etiqueta, font=("Helvetica", 10, "bold")).grid(row=parent.grid_size()[1], column=0, sticky="w", pady=2)
        ttk.Label(parent, text=valor).grid(row=parent.grid_size()[1]-1, column=1, sticky="w", padx=5)

    crear_linea_stat(frame_resultados, "País más poblado:", f"{pais_max_pob['nombre_comun_es']} ({pais_max_pob['poblacion_num']:,.0f})".replace(',', '.'))
    crear_linea_stat(frame_resultados, "País menos poblado:", f"{pais_min_pob['nombre_comun_es']} ({pais_min_pob['poblacion_num']:,.0f})".replace(',', '.'))
    crear_linea_stat(frame_resultados, "Promedio de población:", f"{promedio_poblacion:,.0f}".replace(',', '.'))
    crear_linea_stat(frame_resultados, "Promedio de superficie:", f"{promedio_superficie:,.2f} km²".replace(',', '.'))

    ttk.Separator(frame_stats, orient='horizontal').pack(fill='x', pady=10)
    ttk.Label(frame_stats, text="Países por Continente", font=("Helvetica", 12, "bold")).pack()
    
    frame_continentes = ttk.Frame(frame_stats)
    frame_continentes.pack(fill="x", pady=5)
    for continente, cantidad in sorted(conteo_continentes.items()): # Muestra el conteo de países por continente ordenado.
        crear_linea_stat(frame_continentes, f"{continente}:", str(cantidad))
    
    ttk.Button(frame_stats, text="Cerrar", command=ventana_stats.destroy).pack(side="bottom", pady=10) # Botón para cerrar la ventana de estadísticas.

# Función de Créditos
def mostrar_creditos():
    """Muestra un mensaje con los nombres de los creadores."""
    messagebox.showinfo( # Muestra un cuadro de diálogo con la información de los créditos.
        "Créditos", 
        "Programa de Visor de Datos de Países\n\nHecho por:\n- Genaro Senatore\n- Exequiel Castro"
    )

# Función Principal de la Interfaz
def iniciar_interfaz():
    """Crea y ejecuta la interfaz gráfica principal."""
    global dataset_paises, combo_ordenar, tree, ventana, texto_busqueda_var
    
    ventana = tk.Tk() # Crea la ventana principal.
    ventana.title("Visor de Datos de Países")
    ventana.geometry("1000x600")

    ruta_csv = os.path.join("Continentes", "Todos.csv") # Define la ruta del archivo de datos.
    dataset_paises = cargar_datos_en_memoria(ruta_csv) # Carga los datos.
    
    if dataset_paises is None: # Si falla la carga, inicializa vacío.
        dataset_paises = []

    # Paneles
    frame_izquierda = ttk.Frame(ventana, width=200) # Crea el marco para los controles (panel izquierdo).
    frame_derecha = ttk.Frame(ventana) # Crea el marco para la tabla de datos (panel derecho).
    frame_izquierda.pack(side="left", fill="y", padx=10, pady=10)
    frame_derecha.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Panel Izquierdo
    ttk.Label(frame_izquierda, text="Menú de Acciones", font=("Helvetica", 12, "bold")).pack(pady=10)
    
    ttk.Separator(frame_izquierda, orient='horizontal').pack(fill='x', pady=10)

    # Búsqueda de un país
    ttk.Label(frame_izquierda, text="Buscar País por Nombre:").pack(pady=(5,0))
    texto_busqueda_var = tk.StringVar() # Inicializa la variable de control para la búsqueda.
    entry_busqueda = ttk.Entry(frame_izquierda, textvariable=texto_busqueda_var) # Campo de entrada de búsqueda.
    entry_busqueda.pack(fill="x", padx=5)

    columnas_a_mostrar_busqueda = {"nombre_comun_es": "Nombre", "poblacion": "Población", "area": "Superficie", "continente": "Continente"}
    nombres_internos_columnas_busqueda = list(columnas_a_mostrar_busqueda.keys())

    ttk.Button(frame_izquierda, 
               text="Buscar", 
               command=lambda: buscar_pais(tree, dataset_paises, nombres_internos_columnas_busqueda, texto_busqueda_var) # Botón para iniciar la búsqueda.
    ).pack(fill="x", pady=5)
    
    ttk.Button(frame_izquierda, 
               text="Mostrar Todos", 
               command=lambda: [texto_busqueda_var.set(""), mostrar_datos_en_treeview(tree, dataset_paises, nombres_internos_columnas_busqueda)] # Botón para borrar la búsqueda y mostrar todos los datos.
    ).pack(fill="x", pady=5)
    
    ttk.Separator(frame_izquierda, orient='horizontal').pack(fill='x', pady=10)

    # Filtrar países
    ttk.Button(frame_izquierda, 
               text="Filtrar Países por Criterio", 
               command=mostrar_ventana_filtro # Botón que abre la ventana de filtros.
    ).pack(fill="x", pady=5)

    ttk.Separator(frame_izquierda, orient='horizontal').pack(fill='x', pady=10)
    
    # Controles de ordenamiento
    ttk.Label(frame_izquierda, text="Ordenar por:").pack(pady=(10,0))
    opciones_orden = ["Nombre", "Población", "Superficie", "Continente"]
    combo_ordenar = ttk.Combobox(frame_izquierda, values=opciones_orden, state="readonly") # Menú desplegable para seleccionar el criterio de ordenamiento.
    combo_ordenar.pack(fill="x", padx=5)
    combo_ordenar.set(opciones_orden[0]) # Selecciona Nombre por defecto
    
    ttk.Button(frame_izquierda, 
               text="Ordenar Ascendente", 
               command=lambda: ordenar_desde_controles(es_descendente=False) # Botón de orden ascendente.
    ).pack(fill="x", pady=(5, 2))
    
    ttk.Button(frame_izquierda, 
               text="Ordenar Descendente", 
               command=lambda: ordenar_desde_controles(es_descendente=True) # Botón de orden descendente.
    ).pack(fill="x", pady=(0, 5))
    
    ttk.Separator(frame_izquierda, orient='horizontal').pack(fill='x', pady=10)
    
    # Botón de Estadísticas
    ttk.Button(frame_izquierda, text="Mostrar Estadísticas", command=mostrar_ventana_estadisticas).pack(fill="x", pady=5) # Botón que abre la ventana de estadísticas.
    
    # Botón de Créditos
    ttk.Button(frame_izquierda, text="Créditos", command=mostrar_creditos).pack(fill="x", pady=5) # Botón que muestra los créditos.
    
    # Panel Derecho (Tabla de datos)
    ttk.Label(frame_derecha, text="Países del Mundo", font=("Helvetica", 10)).pack(pady=(0, 5))
    columnas_a_mostrar = {"nombre_comun_es": "Nombre", "poblacion": "Población", "area": "Superficie", "continente": "Continente"}
    nombres_internos_columnas = list(columnas_a_mostrar.keys())
    tree = ttk.Treeview(frame_derecha, columns=nombres_internos_columnas, show="headings") # Crea el widget de tabla (Treeview).
    for internal_name, display_name in columnas_a_mostrar.items():
        tree.heading(internal_name, text=display_name) # Configura el encabezado de cada columna.
        tree.column(internal_name, width=150, anchor='center')
    vsb = ttk.Scrollbar(frame_derecha, orient="vertical", command=tree.yview) # Crea la barra de desplazamiento vertical.
    hsb = ttk.Scrollbar(frame_derecha, orient="horizontal", command=tree.xview) # Crea la barra de desplazamiento horizontal.
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set) # Vincula el Treeview a las barras.
    vsb.pack(side='right', fill='y')
    hsb.pack(side='bottom', fill='x')
    tree.pack(side='left', fill='both', expand=True)

    if dataset_paises:
        mostrar_datos_en_treeview(tree, dataset_paises, nombres_internos_columnas) # Carga los datos iniciales en la tabla.

    ventana.mainloop() # Inicia el bucle principal de la aplicación gráfica.
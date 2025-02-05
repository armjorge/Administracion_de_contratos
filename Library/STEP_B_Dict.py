
import pandas as pd
import ast

def STEP_B_get_string_populated(df_clientes, tipo): 
    print("\t🛠️ Iniciando la generación del diccionario para el contrato...\n")
    # Crear el diccionario poblado
    orchestration_dict = f"""
    {{
        'Institución': "{STEP_B_populate_from_df(df_clientes, 'EMISOR DEL CONTRATO')}",
        'Contrato': "STEP_A_1_GetDate",
        'Modificatorio': "STEP_A_2_df_fields(df_to_load, 'Proyecto')",
        'Start Date': "STEP_A_2_df_fields(df_to_load, 'Materia')",
        'End Date': "STEP_A_3_GetNote(15)",
        'Estatus': "formalizado",
        'SKU': "funcion_sku(parametros) -> skus = producto: 010.000.4154.00, precio: 207, piezas: 16200"
    }}
    """

    # Mostrar valores antes de devolver el diccionario
    print("\n🔹 Diccionario generado con valores actuales:")
    print(orchestration_dict)
    computer_dict = STEP_B_dict_validation(orchestration_dict)

    return orchestration_dict, computer_dict



def STEP_B_dict_validation(dicct_book):
    try:
        # Step 1: Trim leading/trailing spaces
        dicct_book = dicct_book.strip()

        # Step 2: Fix common syntax issues
        dicct_book = dicct_book.replace("‘", "'").replace("’", "'")  # Smart quotes to normal quotes
        dicct_book = dicct_book.replace("“", '"').replace("”", '"')  # Smart double quotes fix
        
        # Step 3: Count brackets
        open_brackets = dicct_book.count('{')
        close_brackets = dicct_book.count('}')
        
        if open_brackets != close_brackets:
            print(f"⚠️ Desajuste en corchetes: {open_brackets} abiertos, {close_brackets} cerrados.")
            return None

        # Step 4: Try parsing the string into a dictionary
        cleaned_dict = ast.literal_eval(dicct_book)

        if not isinstance(cleaned_dict, dict):
            raise ValueError("⚠️ Error: La estructura no es un diccionario válido.")

        print("✅ Diccionario validado y corregido correctamente.")
        return cleaned_dict

    except (SyntaxError, ValueError) as e:
        print(f"❌ Error al analizar el diccionario: {e}")
        print("⚠️ Revisa los corchetes, comillas y la estructura del diccionario.")
        
        # Suggest a manual fix
        print("\n🔹 Sugerencia: Asegúrate de que el diccionario esté bien formateado:")
        print("{ 'Clave': 'Valor', 'Otra Clave': 'Otro Valor' }")
        return None    

def STEP_B_populate_from_df(df_to_load, column):
    """
    Handles loading a DataFrame from a pickle file, ensuring the specified column exists.
    Allows the user to input or select values.
    
    Parameters:
        df_to_load (str): Path to the pickle file.
        column (str): Column name to retrieve data from.
    
    Returns:
        Selected value from the column.
    """

    # Check if the pickle file exists
    """
    if not os.path.exists(df_to_load):
        print("❌ Archivo no localizado, procedemos a crear uno.")
        df = pd.DataFrame()  # Create an empty DataFrame
        df.to_pickle(df_to_load)
        print("✅ Archivo pickle creado.")
    """
    # Load the DataFrame
    #df = pd.read_pickle(df_to_load)
    if not df_to_load.empty:
        print("✅ Archivo con información cargada.")

    # Ensure the column exists in the DataFrame
    if column not in df_to_load.columns:
        print(f"🔹 Columna '{column}' no encontrada. Abre el excel y generar una nueva columna.")
        #df[column] = pd.Series(dtype="object")  # Add an empty column
        #df.to_pickle(df_to_load)  # Save updated DataFrame
        print(f"✅ Nueva columna '{column}' por crear.")

    # Check if there are any values in the column
    if len(df_to_load[column].dropna()) > 0:
        print("✅ Se encontró al menos un registro:")
        unique_values = df_to_load[column].dropna().unique()
        for idx, value in enumerate(unique_values):
            print(f"\t{idx}) {value}")
    else:
        print(f"❌ No se encontraron registros en la columna {column}.")

    # Main loop for user input
    while True:
        print("\n📌 Opciones:")
        #print(f"\t1) Agregar más valores o actualizar en la columna {column}")
        print(f"\tSeleccionar un valor existente en la columna {column}")
        
        try:
            choice = 2 #int(input("Selecciona una opción (1/2): "))
        except ValueError:
            print("⚠️ Entrada no válida. Ingresa 1 o 2.")
            continue

        if choice == 1:
            # Save the column to a CSV for user input
            csv_path = os.path.join(os.path.dirname(df_to_load), f"{column}.csv")
            df_to_load[[column]].to_csv(csv_path, index=False)
            print(f"📂 Se generó el archivo: {csv_path}")
            print("📂 Búscalo en tu CODE o desarrolla código para abrirlo en cualquier sistema")
            input("📝 Agrega nuevos valores en el archivo CSV y presiona ENTER cuando termines...")

            # Reload the updated CSV
            updated_df = pd.read_csv(csv_path)

            df_to_load[column] = updated_df[column]  # Replace column data
            #df_to_load.to_pickle(df_to_load)  # Save changes
            print("✅ DataFrame maestro actualizado con estos datos: ")
            print("\n🔹 Valores disponibles:")
            unique_values = df_to_load[column].dropna().unique()
            for idx, value in enumerate(unique_values):
                print(f"\t{idx}) {value}")
            os.remove(csv_path)
            print("✅ CSV de la captura eliminado")
                            
        elif choice == 2:
            # Let the user choose a value from the list
            unique_values = df_to_load[column].dropna().unique()
            if len(unique_values) == 0:
                print("⚠️ No hay valores disponibles para seleccionar.")
                continue
            
            print("\n🔹 Valores disponibles:")
            for idx, value in enumerate(unique_values):
                print(f"\t{idx}) {value}")

            try:
                index = int(input("🔹 Dame el índice del valor: "))
                if index in range(len(unique_values)):
                    return unique_values[index]
                else:
                    print("⚠️ Índice fuera de rango.")
            except ValueError:
                print("⚠️ Entrada no válida. Ingresa un número válido.")

        else:
            print("⚠️ Opción no válida. Intenta de nuevo.")
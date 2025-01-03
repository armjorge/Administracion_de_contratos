import os
import re
from PyPDF2 import PdfReader
import logging
import string

# Suppress warnings from PyPDF2
logging.getLogger("PyPDF2").setLevel(logging.ERROR)

def main():
    source_directory = r'C:\Users\armjorge\Dropbox\3. Armando Cuaxospa\Reportes GPT 2025\Administración de contratos'
    
    patterns = {
        "primal_contract_pattern": {
            "Contract Code": str,
            "Institution": str,
            "Start Date": "dd/mm/yyyy",
            "End Date": "dd/mm/yyyy",
            "Type": ["formalizado", "no formalizado"],
            "SKU": dict,  # {'sku': (pieces, price)}
            "Calendario": ["true", "false"]
        },
        "modificatory_contract_pattern": {
            "Primigenio": str,
            "Modificatorio": str,
            "Institution": str,
            "Start Date": "dd/mm/yyyy",
            "End Date": "31/12/2024",
            "Type": ["formalizado", "no formalizado"],
            "SKU": dict,  # {'sku': (pieces, price)}
            "Calendario": ["true", "false"]
        }
    }
    user_input = input("¿Qué deseas hacer?\n1. Cargar un nuevo contrato a la base\n2. [To be developed]\nIngrese el número de la opción: ")
    
    if user_input == "1":
        dict_data_to_process = A_Dict_new_files(source_directory, patterns)
        if dict_data_to_process is None:
            print("\nNo se encontraron archivos para procesar.")
        else:
            print("\nArchivos para procesar:")
            dict_data_to_process = A2_rename_files(dict_data_to_process, source_directory)

            print("\nIniciando Renombrado y Movimiento de archivos\n")
            formalizados_path = {"formalizado": os.path.join(source_directory, "Formalizados")}
            no_formalizados_path = {"no formalizado": os.path.join(source_directory, "No formalizados")}
            B_rename_and_move(dict_data_to_process, formalizados_path, no_formalizados_path)

            
def A_Dict_new_files(source_directory, patterns):
    # Define the temporary danger path
    temp_path = os.path.join(source_directory, "Temp-danger")
    

    # Check if temp_path exists and has files inside
    if os.path.exists(temp_path):
        if any(os.scandir(temp_path)):
            print("\nLa carpeta 'Temp-danger' ya contiene archivos.")
            print("Revise los archivos en esta carpeta antes de continuar. Terminando el script.")
            return None
    else:
        # Create temp_path if it doesn't exist
        os.makedirs(temp_path)
        print("\nLa carpeta 'Temp-danger' ha sido creada.")

    input("\nSube el o los PDFs rotulados a la carpeta 'Temp-danger' y presiona Enter para continuar...")

    # List all PDF files in temp_path
    pdf_files = [os.path.join(temp_path, f) for f in os.listdir(temp_path) if f.endswith('.pdf')]

    if not pdf_files:
        print("\nNo se detectaron archivos PDF en la carpeta 'Temp-danger'. Intente nuevamente.")
        return A_Feed_new_file(source_directory, patterns)  # Restart the process

    # Process the PDF files using A1_extract_pattern
    ok_pdf_files, not_ok_files = A1_extract_pattern(pdf_files, patterns)
    print(ok_pdf_files)
    if not ok_pdf_files:
        print("\nNo hay archivos válidos para continuar.")
        return None

    print("\nArchivos con patrones válidos encontrados. Procediendo a renombrarlos...")
    renamed_files = A2_rename_files(ok_pdf_files, source_directory)

    return renamed_files

def A1_extract_pattern(PDF_files, patterns):
    # Suppress PyPDF2 logging
    logging.getLogger("PyPDF2").setLevel(logging.ERROR)

    ok_pdf_files = {}
    not_ok_files = []

    # Define regex for detecting the pattern type Esto no me deja tranquilo, creo que podemos construirlos dinámicamente. Por ahora continuemos. 
    primal_identifier = "Contract Code"
    modificatory_identifier = "Primigenio"

    for pdf_file in PDF_files:
        try:
            reader = PdfReader(pdf_file)
            text = ''.join(page.extract_text() for page in reader.pages)

            # Find the line with a potential pattern
            match = re.search(r'\{.*\}', text)
            if match:
                matched_text = match.group()
                # Identify the pattern type
                if primal_identifier in matched_text:
                    pattern_name = "primal_contract_pattern"
                elif modificatory_identifier in matched_text:
                    pattern_name = "modificatory_contract_pattern"
                else:
                    print(f"El archivo {os.path.basename(pdf_file)} no coincide con ningún patrón conocido.")
                    not_ok_files.append(pdf_file)
                    continue

                # Validate fields for the identified pattern
                missing_fields = []
                mismatched_fields = []
                expected_fields = patterns[pattern_name]

                for field, expected_type in expected_fields.items():
                    field_match = re.search(fr"{field}: (.*?)(,|}})", matched_text)
                    if not field_match:
                        missing_fields.append(field)
                    else:
                        field_value = field_match.group(1).strip()
                        # Validate the field's value type or format
                        if isinstance(expected_type, list) and field_value not in expected_type:
                            mismatched_fields.append(f"{field}: {field_value}")
                        elif expected_type == "dd/mm/yyyy":
                            if not re.match(r"\d{2}/\d{2}/\d{4}", field_value):
                                mismatched_fields.append(f"{field}: {field_value}")

                if not missing_fields and not mismatched_fields:
                    ok_pdf_files[pdf_file] = {"pattern": pattern_name, "content": matched_text}
                else:
                    if missing_fields:
                        print(f"El archivo {os.path.basename(pdf_file)} tiene campos faltantes: {missing_fields}")
                    if mismatched_fields:
                        print(f"El archivo {os.path.basename(pdf_file)} tiene campos con valores no válidos: {mismatched_fields}")
                    not_ok_files.append(pdf_file)
            else:
                print(f"El archivo {os.path.basename(pdf_file)} no contiene rótulo")
                not_ok_files.append(pdf_file)

        except Exception as e:
            print(f"Error procesando {pdf_file}: {e}")
            not_ok_files.append(pdf_file)

    return ok_pdf_files, not_ok_files

def A2_rename_files(ok_pdf_files, source_directory):
    """
    Prepares metadata for renaming files.
    """
    renamed_files = {}

    # Helper function to sanitize filenames
    def sanitize_filename(name):
        allowed_chars = string.ascii_letters + string.digits + " .-_"
        return ''.join(c for c in name if c in allowed_chars)

    for file_path, data in ok_pdf_files.items():
        pattern = data["pattern"]
        content = data["content"]

        # Construct filename based on the pattern type
        if pattern == "primal_contract_pattern":
            contract_code = re.search(r'Contract Code: (.*?),', content)
            institution = re.search(r'Institution: (.*?),', content)
            type_field = re.search(r'Type: (formalizado|no formalizado)', content)

            contract_code = sanitize_filename(contract_code.group(1)) if contract_code else ""
            institution = sanitize_filename(institution.group(1)) if institution else ""
            type_field = sanitize_filename(type_field.group(1)) if type_field else ""

            filename = f"{contract_code}_{institution}_{type_field}.pdf"

        elif pattern == "modificatory_contract_pattern":
            primigenio = re.search(r'Primigenio: (.*?),', content)
            modificatorio = re.search(r'Modificatorio: (.*?),', content)
            institution = re.search(r'Institution: (.*?),', content)
            type_field = re.search(r'Type: (formalizado|no formalizado)', content)

            primigenio = sanitize_filename(primigenio.group(1)) if primigenio else ""
            modificatorio = sanitize_filename(modificatorio.group(1)) if modificatorio else ""
            institution = sanitize_filename(institution.group(1)) if institution else ""
            type_field = sanitize_filename(type_field.group(1)) if type_field else ""

            filename = f"{primigenio}_{modificatorio}_{institution}_{type_field}.pdf"

        else:
            print(f"Patrón desconocido para el archivo {file_path}. Saltando...")
            continue

        # Prepare data for moving
        renamed_files[file_path] = {
            "renamed": filename,
            "pattern": pattern,
            "content": content,
            "final_path": None  # To be set in `B_rename_and_move`
        }

    print("Archivos preparados para renombrar:")
    for original, data in renamed_files.items():
        print(f"{original} -> {data['renamed']}")

    return renamed_files

def B_rename_and_move(dict_with_data_to_process, *paths_by_type):
    """
    Renames and moves files based on their 'Type' and the provided destination paths.
    """
    for file_path, data in dict_with_data_to_process.items():
        renamed_file = data["renamed"]
        file_type = re.search(r'Type: (formalizado|no formalizado)', data["content"]).group(1)

        # Determine the destination folder
        destination_folder = None
        for type_dict in paths_by_type:
            if file_type in type_dict:
                destination_folder = type_dict[file_type]
                break

        if destination_folder:
            os.makedirs(destination_folder, exist_ok=True)
            destination_path = os.path.join(destination_folder, renamed_file)

            # Check if the file exists before renaming and moving
            if os.path.exists(file_path):
                os.rename(file_path, destination_path)
                data["final_path"] = destination_path
                print(f"Archivo '{renamed_file}' movido a '{destination_folder}'")
            else:
                print(f"El archivo '{file_path}' no se encontró. Es posible que ya haya sido procesado.")
        else:
            print(f"Type: '{file_type}' no considerado en las carpetas.")

if __name__ == "__main__":
    main()

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

    dict_data_to_process = A_Feed_new_file(source_directory, patterns)
    
    if dict_data_to_process is None:
        print("\nNo se encontraron archivos para procesar.")
    else:
        print("\nArchivos para procesar:")
        for key, value in dict_data_to_process.items():
            relative_path = key.replace(source_directory + os.sep, "")
            print(f"{relative_path}: {value}\n")


def A_Feed_new_file(source_directory, patterns):
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

    if not ok_pdf_files:
        print("\nNo hay archivos válidos para continuar.")
        return None

    print("\nArchivos con patrones válidos encontrados. Procediendo a renombrarlos...")
    renamed_files = A2_rename_files(ok_pdf_files)

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



def A2_rename_files(ok_pdf_files):
    renamed_files = {}

    # Helper function to sanitize filenames
    def sanitize_filename(name):
        allowed_chars = string.ascii_letters + string.digits + " .-_"
        return ''.join(c for c in name if c in allowed_chars)

    for file_path, data in ok_pdf_files.items():
        pattern = data["content"]

        # Extract fields for filename construction
        contract_code = re.search(r'Contract Code: (.*?),', pattern)
        modificatorio = re.search(r'Modificatorio: (.*?),', pattern)
        type_field = re.search(r'Type: (formalizado|no formalizado)', pattern)

        # Sanitize extracted fields
        contract_code = sanitize_filename(contract_code.group(1)) if contract_code else ""
        modificatorio = sanitize_filename(modificatorio.group(1)) if modificatorio else ""
        type_field = sanitize_filename(type_field.group(1)) if type_field else ""

        # Construct filename
        filename = f"{contract_code}_{modificatorio}_{type_field}.pdf" if modificatorio else f"{contract_code}_{type_field}.pdf"

        # Check for duplicates
        if filename in renamed_files.values():
            print(f"Archivo duplicado detectado: {filename} en {file_path}")
            print("\nElimine el duplicado antes de continuar. Terminando el script.")
            return None

        # Add to renamed files
        renamed_files[file_path] = filename

    # Print renamed files
    print("A2 rename files has finished. Archivos renombrados:")
    for original, renamed in renamed_files.items():
        print(f"{original} -> {renamed}")

    return renamed_files

if __name__ == "__main__":
    main()

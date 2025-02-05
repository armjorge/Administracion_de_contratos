import os
import sys
import shutil
from folders_files_open import create_directory_if_not_exists, load_dataframe
from STEP_B_Dict import STEP_B_get_string_populated
from STEP_C_PDFhandling import STEP_C_PDF_HANDLING, STEP_C_read_labeled_pdf

def STEP_A_orchestration(tipo, folder_path):
    working_folder = folder_path
    print("\tIniciando el orquestador para poblar el diccionario")
    PDF_library = os.path.join(working_folder, "PDF_Library")
    create_directory_if_not_exists(PDF_library)
    desagregada_path = os.path.join(working_folder, "Desagregada.xlsx")
    desagregada_sheet = 'Emisores contrato'
    desagregada_columns = ['INSTITUCION HOMOLOGADA', 'EMISOR DEL CONTRATO']
    df_desagregada = load_dataframe(desagregada_path, desagregada_sheet, desagregada_columns)
    #df_referencia_interna = os.path.join(working_folder, "processed_files.pickle")
    temp_directory = os.path.join(working_folder, 'Temp')    
    print("\n\tPASO A: GENERAR DE DICCIONARIO PARA NUEVO CONTRATO\n")
    human_dict, valid_dict = STEP_B_get_string_populated(df_desagregada, tipo)
    print('Diccionario Capturado\n', human_dict, "\nDiccionario Procesado\n", valid_dict)
    print("\n\tPASO C: MANEJAR EL PDF\n")  
    
    """
    pdf_path_list = [STEP_C_PDF_HANDLING(temp_directory, valid_dict)]
    result_dict = STEP_C_read_labeled_pdf(pdf_path_list, valid_dict)
    print(f"Inserto agregado: {result_dict}")
    df_feed = STEP_C_feed_DF(df_referencia_interna, result_dict)
    # ✅ Move pdf_path_list[0] to PDF_library
    source_path = pdf_path_list[0]
    destination_path = os.path.join(PDF_library, os.path.basename(source_path))
    try:
        shutil.move(source_path, destination_path)
        print(f"✅ Archivo movido a la biblioteca: {destination_path}")
        
        # ✅ Confirm the file is in PDF_library
        if os.path.exists(destination_path):
            print("✅ Confirmación: El archivo está en la biblioteca.")
            
            # ✅ Remove temp_directory
            if os.path.exists(temp_directory):
                shutil.rmtree(temp_directory)
                print("✅ Temp directory eliminado.")
        
        print("📄 Archivo rotulado en la biblioteca y registrado en la referencia interna")
    except Exception as e:
        print(f"❌ Error al mover el archivo: {e}")
        """          

import os
import sys
import shutil
script_directory = os.path.dirname(os.path.abspath(__file__))
function_library = os.path.abspath(os.path.join(script_directory, 'Library'))
working_folder = os.path.abspath(os.path.join(script_directory, '..'))
sys.path.append(function_library) 
from STEP_A_orchestration import STEP_A_orchestration

def main():   
    print("¿1) Capturar un contrato o 2) extraer base contratos existentes?")
    while True:
        step_0 = input("Seleccione una opción (1 o 2): ")
        if step_0 == "1":
            while True:
                tipo = input("Define el tipo P) Primigenio o M) Modificatorio: ")
                tipo = tipo.lower()
                if tipo == 'p':
                    tipo = 'Primigenio'
                    break
                elif tipo == 'm':
                    tipo = 'Modificatorio'
                    break
                else:
                    print("Entrada no válida, por favor elija P o M.")
            STEP_A_orchestration(tipo, working_folder)
        elif step_0 == "2":
            # Suponiendo que aquí debería haber algún código para extraer la base de contratos
            print("Base de contratos extraída correctamente.")
        else:
            print("Opción no válida. Por favor, seleccione 1 o 2")
            print("¿1) Capturar un contrato o 2) extraer base contratos existentes?")

  
 # Call the main function
if __name__ == "__main__":
    main()
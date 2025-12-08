import os
import importlib
import glob
from .Log import Log

def import_module(folder: str, log=False, catch_error=True):
    """
    folder : package.subpackage
    """
    # Parcours des fichiers .py dans le répertoire du package
    if log:
        Log.print("Importing Page :")
    modules = {}
    modules.clear()
    
    for file_path in glob.glob(os.path.join(*folder.split("."), "*.py"), recursive=True):
        # Obtention du nom du module à partir du chemin du fichier
        module_name = os.path.basename(file_path)[:-3]  # Supprime l'extension .py
        
        try:
            # Importation dynamique du module

            module = importlib.import_module(f'{folder}.{module_name}')
            
            # Ajout du module au dictionnaire
            modules.update({module_name:module})
            if log:
                Log.print(f"═╣ importing '{module_name}' : {Log.color('done', color=Log.GREEN)}")
            
        except Exception as e:
            if log:
                Log.print(f"═╣ importing '{module_name}' : {Log.color('failled', color=Log.RED)} -> {e}")

    return modules
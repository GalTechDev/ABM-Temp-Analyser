from flask import Flask
from .devtool import Page, import_module


welcome =   """                               
            """
###################################################################################################
# GENERAL CONFIGURATION
###################################################################################################

# Répertoire du package contenant les modules
page_directory = "web.page.py"
template_directory = "web/page/html"

# Dictionnaire pour stocker les modules importés
list_modules = {}

app = Flask(__name__, template_folder=template_directory)
app.secret_key = "iamsecret"  # for debug
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

###################################################################################################
# ENTRY POINT
###################################################################################################

if __name__ == "__main__":
    # opens the web app in debug mode for local connections only
    print(welcome)   
    list_modules = import_module(page_directory, log=True)
    Page.compile_page(app)
    app.config['SERVER_NAME'] = "localhost:8001"
    app.name = app.config['SERVER_NAME']
    app.run(debug=True, host="localhost", port=8001)

else:
    print(welcome)
    list_modules = import_module(page_directory, log=True)
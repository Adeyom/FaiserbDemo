from flask import Flask
from flask_cors import CORS
# from pyngrok import ngrok


def create_app():
    app = Flask(__name__)
    # #Ngrok server
    # public_url = ngrok.connect(5000)
    # print(f" * Ngrok URL: {public_url}")

    # # Guardar la URL pública para usar en el resto de la app
    # app.config["BASE_URL"] = public_url

    CORS(app)
    # Configuración opcional
    app.config['SECRET_KEY'] = 'tu_clave_secreta'
    
    # Registro de rutas desde routes.py
    from .routes import main
    app.register_blueprint(main)
    
    return app

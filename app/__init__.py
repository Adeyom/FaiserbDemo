from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    CORS(app)

    # Configuración opcional
    app.config['SECRET_KEY'] = 'tu_clave_secreta'
    
    # Registro de rutas desde routes.py
    from .routes import main
    app.register_blueprint(main)
    
    return app

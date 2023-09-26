from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
import os


swagger_config = {
    "headers": [
        ('Access-Control-Allow-Origin', '*'),
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "title": 'Clean IDE - Users API',
    "description": 'This API is part of an MVP made for the 3rd Sprint of the Fullstack Developper graduate course at PUC-RJ',
    "termsOfService": 'Termos de Serviço',
    "contact": {
        "email": "vinians2006@yahoo.com.br"
    },
    "license": {
        "name": "Licença",
        "url": ""
    },
}

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
SECRET_KEY = os.getenv("SECRET_KEY")
swagger = Swagger(app=app, config=swagger_config)
CORS(app, origins='*', methods='*', allow_headers='*')

from controller import *

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5002))
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=port, debug=True)

import os
from flask import Flask
from app.models import db

def create_app():
    app = Flask(__name__)

    # Configuração
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "estoque.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"

    # Inicializar extensões
    db.init_app(app)

    # Registrar blueprints
    from app.blueprints import main_bp, produtos_bp, movimentos_bp, caixa_bp, relatorios_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(movimentos_bp)
    app.register_blueprint(caixa_bp)
    app.register_blueprint(relatorios_bp)

    # Criar tabelas
    with app.app_context():
        db.create_all()

    return app

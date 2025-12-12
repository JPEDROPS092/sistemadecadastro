import os
from flask import Flask
from flask_login import LoginManager
from app.models import db, Usuario

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

    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar blueprints
    from app.blueprints import main_bp, produtos_bp, movimentos_bp, caixa_bp, relatorios_bp
    from app.blueprints.auth import auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(movimentos_bp)
    app.register_blueprint(caixa_bp)
    app.register_blueprint(relatorios_bp)

    # Criar tabelas e usuários padrão
    with app.app_context():
        db.create_all()

        # Criar usuários padrão se não existirem
        from app.services.auth_service import AuthService
        AuthService.criar_usuarios_padrao()

    return app

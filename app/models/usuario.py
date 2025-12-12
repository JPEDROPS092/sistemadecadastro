from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'admin', 'gerente', 'operador'
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Usuario {self.username}>'

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_admin(self):
        return self.tipo == 'admin'

    @property
    def is_gerente(self):
        return self.tipo in ['admin', 'gerente']

    @property
    def is_operador(self):
        return self.tipo == 'operador'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nome_completo': self.nome_completo,
            'email': self.email,
            'tipo': self.tipo,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None
        }

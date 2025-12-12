from datetime import datetime
from app.models import db
from app.models.usuario import Usuario

class AuthService:
    @staticmethod
    def criar_usuario(username, senha, nome_completo, email, tipo='operador'):
        if Usuario.query.filter_by(username=username).first():
            raise ValueError("Nome de usuário já existe")

        if Usuario.query.filter_by(email=email).first():
            raise ValueError("Email já cadastrado")

        usuario = Usuario(
            username=username,
            nome_completo=nome_completo,
            email=email,
            tipo=tipo
        )
        usuario.set_senha(senha)

        db.session.add(usuario)
        db.session.commit()
        return usuario

    @staticmethod
    def autenticar(username, senha):
        usuario = Usuario.query.filter_by(username=username, ativo=True).first()

        if usuario and usuario.verificar_senha(senha):
            usuario.ultimo_acesso = datetime.utcnow()
            db.session.commit()
            return usuario

        return None

    @staticmethod
    def listar_usuarios():
        return Usuario.query.all()

    @staticmethod
    def obter_usuario(id):
        return Usuario.query.get(id)

    @staticmethod
    def obter_usuario_por_username(username):
        return Usuario.query.filter_by(username=username).first()

    @staticmethod
    def atualizar_usuario(id, **kwargs):
        usuario = Usuario.query.get(id)
        if not usuario:
            return None

        for key, value in kwargs.items():
            if key == 'senha' and value:
                usuario.set_senha(value)
            elif hasattr(usuario, key) and key != 'senha_hash':
                setattr(usuario, key, value)

        db.session.commit()
        return usuario

    @staticmethod
    def desativar_usuario(id):
        usuario = Usuario.query.get(id)
        if usuario:
            usuario.ativo = False
            db.session.commit()
            return True
        return False

    @staticmethod
    def criar_usuarios_padrao():
        """Cria 3 usuários padrões se não existirem"""
        usuarios_padrao = [
            {
                'username': 'admin',
                'senha': 'admin123',
                'nome_completo': 'Administrador do Sistema',
                'email': 'admin@sistema.com',
                'tipo': 'admin'
            },
            {
                'username': 'gerente',
                'senha': 'gerente123',
                'nome_completo': 'Gerente do Sistema',
                'email': 'gerente@sistema.com',
                'tipo': 'gerente'
            },
            {
                'username': 'operador',
                'senha': 'operador123',
                'nome_completo': 'Operador do Sistema',
                'email': 'operador@sistema.com',
                'tipo': 'operador'
            }
        ]

        for user_data in usuarios_padrao:
            existing = Usuario.query.filter_by(username=user_data['username']).first()
            if not existing:
                try:
                    AuthService.criar_usuario(**user_data)
                    print(f"✓ Usuário '{user_data['username']}' criado com sucesso")
                except Exception as e:
                    print(f"✗ Erro ao criar usuário '{user_data['username']}': {e}")

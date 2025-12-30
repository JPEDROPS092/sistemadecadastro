"""
Configuração base para os testes
"""
import pytest
import tempfile
import os
import sys

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Usuario, Produto, Caixa, Movimento, MovimentoCaixa
from app.services.auth_service import AuthService


@pytest.fixture
def app():
    """Fixture que cria uma instância da aplicação para testes"""
    # Cria um banco temporário
    db_fd, db_path = tempfile.mkstemp()
    
    # Configuração de teste
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    
    # Cria a aplicação
    app = create_app()
    app.config.update(test_config)
    
    with app.app_context():
        db.create_all()
        # Sempre criar usuários de teste (banco limpo a cada fixture)
        try:
            AuthService.criar_usuario(
                username='admin_test',
                senha='123456',
                nome_completo='Admin Teste',
                email='admin@test.com',
                tipo='admin'
            )
            AuthService.criar_usuario(
                username='operador_test',
                senha='123456',
                nome_completo='Operador Teste',
                email='operador@test.com',
                tipo='operador'
            )
        except ValueError:
            # Usuários já existem, limpar e recriar
            db.drop_all()
            db.create_all()
            AuthService.criar_usuario(
                username='admin_test',
                senha='123456',
                nome_completo='Admin Teste',
                email='admin@test.com',
                tipo='admin'
            )
            AuthService.criar_usuario(
                username='operador_test',
                senha='123456',
                nome_completo='Operador Teste',
                email='operador@test.com',
                tipo='operador'
            )
        
    yield app
    
    # Cleanup
    with app.app_context():
        db.drop_all()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Fixture que cria um cliente de teste"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture que cria um runner CLI"""
    return app.test_cli_runner()


@pytest.fixture
def admin_user(app):
    """Fixture que retorna um usuário admin para testes"""
    with app.app_context():
        return Usuario.query.filter_by(username='admin_test').first()


@pytest.fixture
def operador_user(app):
    """Fixture que retorna um usuário operador para testes"""
    with app.app_context():
        return Usuario.query.filter_by(username='operador_test').first()


@pytest.fixture
def authenticated_admin_client(client, admin_user):
    """Fixture que retorna um cliente autenticado como admin"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin_user.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def authenticated_operador_client(client, operador_user):
    """Fixture que retorna um cliente autenticado como operador"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(operador_user.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def produto_teste(app):
    """Fixture que cria um produto para testes"""
    with app.app_context():
        produto = Produto(
            nome='Produto Teste',
            valor_compra=10.0,
            valor_venda=15.0,
            quantidade=100,
            estoque_minimo=10
        )
        db.session.add(produto)
        db.session.commit()
        produto_id = produto.id
        db.session.expunge(produto)  # Remove da sessão para evitar detached
        # Retorna o ID para que os testes possam buscar novamente
        return produto_id


@pytest.fixture
def get_produto_teste():
    """Helper fixture para obter o produto teste dentro do contexto do teste"""
    def _get_produto(produto_id):
        return Produto.query.get(produto_id)
    return _get_produto


@pytest.fixture
def caixa_aberto(app, admin_user):
    """Fixture que cria um caixa aberto para testes"""
    with app.app_context():
        caixa = Caixa(
            saldo_inicial=100.0,
            observacao_abertura='Caixa de teste'
        )
        db.session.add(caixa)
        db.session.commit()
        caixa_id = caixa.id
        db.session.expunge(caixa)
        return caixa_id


@pytest.fixture  
def get_caixa_aberto():
    """Helper fixture para obter o caixa aberto dentro do contexto do teste"""
    def _get_caixa(caixa_id):
        return Caixa.query.get(caixa_id)
    return _get_caixa


@pytest.fixture
def movimento_teste(app, produto_teste):
    """Fixture que cria um movimento para testes"""
    with app.app_context():
        movimento = Movimento(
            produto_id=produto_teste,  # produto_teste já é um ID agora
            tipo='entrada',
            quantidade=50,
            valor_unitario=10.0,
            valor_total=500.0,
            observacao='Movimento de teste'
        )
        db.session.add(movimento)
        db.session.commit()
        movimento_id = movimento.id
        db.session.expunge(movimento)
        return movimento_id


@pytest.fixture  
def get_movimento_teste():
    """Helper fixture para obter o movimento teste dentro do contexto do teste"""
    def _get_movimento(movimento_id):
        return Movimento.query.get(movimento_id)
    return _get_movimento


class AuthActions:
    """Classe auxiliar para ações de autenticação nos testes"""
    
    def __init__(self, client):
        self._client = client
    
    def login(self, username='admin_test', senha='123456'):
        """Realiza login"""
        return self._client.post('/auth/login', data={
            'username': username,
            'senha': senha
        })
    
    def logout(self):
        """Realiza logout"""
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """Fixture que retorna objeto para ações de autenticação"""
    return AuthActions(client)
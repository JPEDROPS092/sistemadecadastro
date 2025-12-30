"""
Testes para o módulo de autenticação
"""
import pytest
import sys
import os

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Usuario, db
from app.services.auth_service import AuthService


class TestAuthBlueprint:
    """Testes para as rotas de autenticação"""
    
    def test_login_page_loads(self, client):
        """Testa se a página de login carrega corretamente"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_successful_login(self, client, admin_user):
        """Testa login com credenciais válidas"""
        response = client.post('/auth/login', data={
            'username': 'admin_test',
            'senha': '123456'
        })
        assert response.status_code == 302  # Redirect após login
        
        # Verifica se redirecionou para a página principal
        assert response.location.endswith('/')
    
    def test_invalid_login(self, client):
        """Testa login com credenciais inválidas"""
        response = client.post('/auth/login', data={
            'username': 'usuario_inexistente',
            'senha': 'senha_errada'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'inv' in response.data.lower()  # Mensagem de erro
    
    def test_logout(self, client, auth):
        """Testa logout"""
        # Primeiro faz login
        auth.login()
        
        # Depois faz logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'desconectado' in response.data.lower()
    
    def test_redirect_when_already_logged_in(self, authenticated_admin_client):
        """Testa redirecionamento quando já está logado"""
        response = authenticated_admin_client.get('/auth/login')
        assert response.status_code == 302
        assert response.location.endswith('/')
    
    def test_admin_can_access_users_list(self, authenticated_admin_client):
        """Testa se admin pode acessar lista de usuários"""
        response = authenticated_admin_client.get('/auth/usuarios')
        assert response.status_code == 200
        assert b'admin_test' in response.data
    
    def test_operador_cannot_access_users_list(self, authenticated_operador_client):
        """Testa se operador não pode acessar lista de usuários"""
        response = authenticated_operador_client.get('/auth/usuarios', follow_redirects=True)
        assert response.status_code == 200
        assert b'Acesso negado' in response.data or b'acesso negado' in response.data
    
    def test_create_new_user_as_admin(self, authenticated_admin_client, app):
        """Testa criação de novo usuário como admin"""
        response = authenticated_admin_client.post('/auth/usuarios/novo', data={
            'username': 'novo_usuario',
            'senha': '123456',
            'nome_completo': 'Novo Usuário',
            'email': 'novo@test.com',
            'tipo': 'operador'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se o usuário foi criado
        with app.app_context():
            usuario = Usuario.query.filter_by(username='novo_usuario').first()
            assert usuario is not None
            assert usuario.nome_completo == 'Novo Usuário'
    
    def test_operador_cannot_create_user(self, authenticated_operador_client):
        """Testa se operador não pode criar usuários"""
        response = authenticated_operador_client.get('/auth/usuarios/novo', follow_redirects=True)
        assert response.status_code == 200
        assert b'Acesso negado' in response.data or b'acesso negado' in response.data
    
    def test_profile_access(self, authenticated_admin_client):
        """Testa acesso ao perfil do usuário"""
        response = authenticated_admin_client.get('/auth/perfil')
        assert response.status_code == 200
        assert b'admin_test' in response.data or b'Admin Teste' in response.data
    
    def test_change_password_success(self, authenticated_admin_client, app, admin_user):
        """Testa alteração de senha com sucesso"""
        response = authenticated_admin_client.post('/auth/alterar-senha', data={
            'senha_atual': '123456',
            'senha_nova': '654321',
            'senha_confirmacao': '654321'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se a senha foi alterada
        with app.app_context():
            usuario = Usuario.query.get(admin_user.id)
            assert usuario.verificar_senha('654321')
    
    def test_change_password_wrong_current(self, authenticated_admin_client):
        """Testa alteração de senha com senha atual incorreta"""
        response = authenticated_admin_client.post('/auth/alterar-senha', data={
            'senha_atual': 'senha_errada',
            'senha_nova': '654321',
            'senha_confirmacao': '654321'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'incorreta' in response.data.lower()
    
    def test_change_password_mismatch(self, authenticated_admin_client):
        """Testa alteração de senha com confirmação não coincidente"""
        response = authenticated_admin_client.post('/auth/alterar-senha', data={
            'senha_atual': '123456',
            'senha_nova': '654321',
            'senha_confirmacao': '123456'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'coincidem' in response.data.lower()


class TestAuthService:
    """Testes para o serviço de autenticação"""
    
    def test_autenticar_usuario_valido(self, app, admin_user):
        """Testa autenticação com usuário válido"""
        with app.app_context():
            usuario = AuthService.autenticar('admin_test', '123456')
            assert usuario is not None
            assert usuario.username == 'admin_test'
    
    def test_autenticar_usuario_invalido(self, app):
        """Testa autenticação com usuário inválido"""
        with app.app_context():
            usuario = AuthService.autenticar('usuario_inexistente', 'senha')
            assert usuario is None
    
    def test_autenticar_senha_invalida(self, app):
        """Testa autenticação com senha inválida"""
        with app.app_context():
            usuario = AuthService.autenticar('admin_test', 'senha_errada')
            assert usuario is None
    
    def test_criar_usuario(self, app):
        """Testa criação de usuário"""
        import uuid
        with app.app_context():
            # Usar ID único para evitar conflitos
            unique_id = str(uuid.uuid4())[:8]
            usuario = AuthService.criar_usuario(
                username=f'teste_criacao_{unique_id}',
                senha='123456',
                nome_completo='Teste Criação',
                email=f'teste_{unique_id}@criacao.com',
                tipo='operador'
            )
            
            assert usuario.username == f'teste_criacao_{unique_id}'
            assert usuario.verificar_senha('123456')
            assert usuario.tipo == 'operador'
    
    def test_criar_usuario_duplicado(self, app):
        """Testa criação de usuário com username duplicado"""
        with app.app_context():
            with pytest.raises(Exception):
                AuthService.criar_usuario(
                    username='admin_test',  # Já existe
                    senha='123456',
                    nome_completo='Teste Duplicado',
                    email='duplicado@test.com',
                    tipo='operador'
                )
    
    def test_listar_usuarios(self, app):
        """Testa listagem de usuários"""
        with app.app_context():
            usuarios = AuthService.listar_usuarios()
            assert len(usuarios) >= 2  # admin_test e operador_test
            usernames = [u.username for u in usuarios]
            assert 'admin_test' in usernames
            assert 'operador_test' in usernames
    
    def test_atualizar_usuario(self, app, admin_user):
        """Testa atualização de usuário"""
        with app.app_context():
            AuthService.atualizar_usuario(
                admin_user.id,
                nome_completo='Nome Atualizado',
                email='atualizado@test.com'
            )
            
            usuario = Usuario.query.get(admin_user.id)
            assert usuario.nome_completo == 'Nome Atualizado'
            assert usuario.email == 'atualizado@test.com'
    
    def test_atualizar_senha_usuario(self, app, admin_user):
        """Testa atualização de senha do usuário"""
        with app.app_context():
            AuthService.atualizar_usuario(admin_user.id, senha='nova_senha')
            
            usuario = Usuario.query.get(admin_user.id)
            assert usuario.verificar_senha('nova_senha')
            assert not usuario.verificar_senha('123456')


class TestUsuarioModel:
    """Testes para o modelo Usuario"""
    
    def test_usuario_creation(self, app):
        """Testa criação de usuário"""
        import uuid
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            usuario = Usuario(
                username=f'teste_model_{unique_id}',
                nome_completo='Teste Model',
                email=f'model_{unique_id}@test.com',
                tipo='operador'
            )
            usuario.set_senha('123456')
            
            db.session.add(usuario)
            db.session.commit()
            
            assert usuario.id is not None
            assert usuario.verificar_senha('123456')
            assert not usuario.verificar_senha('senha_errada')
    
    def test_usuario_permissions(self, admin_user, operador_user):
        """Testa permissões do usuário"""
        assert admin_user.is_admin
        assert admin_user.is_gerente
        assert not admin_user.is_operador
        
        assert not operador_user.is_admin
        assert not operador_user.is_gerente
        assert operador_user.is_operador
    
    def test_usuario_to_dict(self, admin_user):
        """Testa conversão para dicionário"""
        user_dict = admin_user.to_dict()
        
        assert user_dict['username'] == 'admin_test'
        assert user_dict['nome_completo'] == 'Admin Teste'
        assert user_dict['tipo'] == 'admin'
        assert 'senha_hash' not in user_dict  # Não deve expor a senha
    
    def test_usuario_repr(self, admin_user):
        """Testa representação string do usuário"""
        repr_str = repr(admin_user)
        assert 'admin_test' in repr_str
        assert 'Usuario' in repr_str
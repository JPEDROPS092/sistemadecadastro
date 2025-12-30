"""
Testes para o módulo de produtos
"""
import pytest
import sys
import os

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Produto, db
from app.services.produto_service import ProdutoService


class TestProdutosBlueprint:
    """Testes para as rotas de produtos"""
    
    def test_produtos_list_requires_auth(self, client):
        """Testa se a listagem de produtos requer autenticação"""
        response = client.get('/produtos/')
        assert response.status_code == 302  # Redirect para login
    
    def test_produtos_list_authenticated(self, authenticated_admin_client, produto_teste):
        """Testa listagem de produtos autenticado"""
        response = authenticated_admin_client.get('/produtos/')
        assert response.status_code == 200
        assert b'Produto Teste' in response.data
    
    def test_create_produto_form_get(self, authenticated_admin_client):
        """Testa acesso ao formulário de criação de produto"""
        response = authenticated_admin_client.get('/produtos/novo')
        assert response.status_code == 200
        assert b'form' in response.data.lower() or b'nome' in response.data.lower()
    
    def test_create_produto_success(self, authenticated_admin_client, app):
        """Testa criação de produto com sucesso"""
        import uuid
        nome_unico = f'Produto Novo {uuid.uuid4().hex[:8]}'
        
        response = authenticated_admin_client.post('/produtos/novo', data={
            'nome': nome_unico,
            'valor_compra': '12.50',
            'valor_venda': '20.00',
            'quantidade': '50',
            'estoque_minimo': '10'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se o produto foi criado
        with app.app_context():
            produto = Produto.query.filter_by(nome=nome_unico).first()
            assert produto is not None
            assert produto.valor_compra == 12.50
            assert produto.valor_venda == 20.00
            assert produto.quantidade == 50
    
    def test_create_produto_invalid_data(self, authenticated_admin_client):
        """Testa criação de produto com dados inválidos"""
        response = authenticated_admin_client.post('/produtos/novo', data={
            'nome': '',  # Nome vazio
            'valor_compra': 'abc',  # Valor inválido
            'valor_venda': '20.00',
            'quantidade': '50'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'erro' in response.data.lower() or b'error' in response.data.lower()
    
    def test_edit_produto_form_get(self, authenticated_admin_client, produto_teste):
        """Testa acesso ao formulário de edição de produto"""
        response = authenticated_admin_client.get(f'/produtos/{produto_teste}/editar')
        assert response.status_code == 200
        assert b'Produto Teste' in response.data
    
    def test_edit_produto_success(self, authenticated_admin_client, produto_teste, app):
        """Testa edição de produto com sucesso"""
        response = authenticated_admin_client.post(f'/produtos/{produto_teste}/editar', data={
            'nome': 'Produto Editado',
            'valor_compra': '15.00',
            'valor_venda': '25.00',
            'estoque_minimo': '5'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se o produto foi editado
        with app.app_context():
            produto = Produto.query.get(produto_teste)
            assert produto.nome == 'Produto Editado'
            assert produto.valor_compra == 15.00
            assert produto.valor_venda == 25.00
    
    def test_edit_nonexistent_produto(self, authenticated_admin_client):
        """Testa edição de produto inexistente"""
        response = authenticated_admin_client.get('/produtos/9999/editar', follow_redirects=True)
        assert response.status_code == 200
        assert b'encontrado' in response.data.lower()
    
    def test_delete_produto_success(self, authenticated_admin_client, app):
        """Testa exclusão de produto com sucesso"""
        # Cria produto para deletar
        with app.app_context():
            produto = Produto(
                nome='Produto Para Deletar',
                valor_compra=10.0,
                valor_venda=15.0,
                quantidade=0,  # Sem estoque para poder deletar
                estoque_minimo=5
            )
            db.session.add(produto)
            db.session.commit()
            produto_id = produto.id
        
        response = authenticated_admin_client.post(f'/produtos/{produto_id}/excluir', follow_redirects=True)
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se o produto foi deletado
        with app.app_context():
            produto = Produto.query.get(produto_id)
            assert produto is None
    
    def test_estoque_baixo(self, authenticated_admin_client, app):
        """Testa listagem de produtos com estoque baixo"""
        # Cria produto com estoque baixo
        with app.app_context():
            produto = Produto(
                nome='Produto Estoque Baixo',
                valor_compra=10.0,
                valor_venda=15.0,
                quantidade=3,  # Abaixo do mínimo
                estoque_minimo=10
            )
            db.session.add(produto)
            db.session.commit()
        
        response = authenticated_admin_client.get('/produtos/estoque-baixo')
        assert response.status_code == 200
        assert b'Produto Estoque Baixo' in response.data


class TestProdutoService:
    """Testes para o serviço de produtos"""
    
    def test_listar_produtos(self, app, produto_teste):
        """Testa listagem de produtos"""
        with app.app_context():
            produtos = ProdutoService.listar_produtos()
            assert len(produtos) >= 1
            assert any(p.nome == 'Produto Teste' for p in produtos)
    
    def test_obter_produto_existente(self, app, produto_teste):
        """Testa obter produto existente"""
        with app.app_context():
            produto = ProdutoService.obter_produto(produto_teste)  # produto_teste é o ID
            assert produto is not None
            assert produto.nome == 'Produto Teste'
    
    def test_obter_produto_inexistente(self, app):
        """Testa obter produto inexistente"""
        with app.app_context():
            produto = ProdutoService.obter_produto(9999)
            assert produto is None
    
    def test_criar_produto(self, app):
        """Testa criação de produto"""
        with app.app_context():
            produto = ProdutoService.criar_produto(
                nome='Produto Service',
                valor_compra=8.0,
                valor_venda=12.0,
                qtd=30,
                estoque_minimo=5
            )
            
            assert produto.nome == 'Produto Service'
            assert produto.valor_compra == 8.0
            assert produto.valor_venda == 12.0
            assert produto.quantidade == 30
            assert produto.estoque_minimo == 5
    
    def test_atualizar_produto(self, app, produto_teste):
        """Testa atualização de produto"""
        with app.app_context():
            produto_atualizado = ProdutoService.atualizar_produto(
                produto_teste,  # produto_teste é o ID
                nome='Produto Atualizado Service',
                valor_venda=18.0
            )
            
            assert produto_atualizado.nome == 'Produto Atualizado Service'
            assert produto_atualizado.valor_venda == 18.0
            # Verifica que o valor de compra original se mantém (10.0 da fixture)
            assert produto_atualizado.valor_compra == 10.0
    
    def test_excluir_produto_sem_movimentos(self, app):
        """Testa exclusão de produto sem movimentos"""
        with app.app_context():
            produto = ProdutoService.criar_produto(
                nome='Produto Para Excluir',
                valor_compra=5.0,
                valor_venda=8.0
            )
            produto_id = produto.id
            
            resultado = ProdutoService.excluir_produto(produto_id)
            assert resultado is True
            
            # Verifica se foi excluído
            produto_excluido = Produto.query.get(produto_id)
            assert produto_excluido is None
    
    def test_produtos_estoque_baixo(self, app):
        """Testa listagem de produtos com estoque baixo"""
        with app.app_context():
            # Cria produto com estoque baixo
            produto1 = ProdutoService.criar_produto(
                nome='Produto Estoque Baixo 1',
                valor_compra=10.0,
                valor_venda=15.0,
                quantidade=2,
                estoque_minimo=10
            )
            
            # Cria produto com estoque OK
            produto2 = ProdutoService.criar_produto(
                nome='Produto Estoque OK',
                valor_compra=10.0,
                valor_venda=15.0,
                quantidade=20,
                estoque_minimo=10
            )
            
            produtos_baixo = ProdutoService.produtos_estoque_baixo()
            nomes_baixo = [p.nome for p in produtos_baixo]
            
            assert 'Produto Estoque Baixo 1' in nomes_baixo
            assert 'Produto Estoque OK' not in nomes_baixo
    
    def test_atualizar_estoque(self, app, produto_teste):
        """Testa atualização de estoque"""
        with app.app_context():
            produto = Produto.query.get(produto_teste)  # produto_teste é o ID
            estoque_inicial = produto.quantidade
            
            # Adiciona ao estoque
            ProdutoService.atualizar_estoque(produto_teste, 20)
            produto = Produto.query.get(produto_teste)
            assert produto.quantidade == estoque_inicial + 20
            
            # Remove do estoque
            ProdutoService.atualizar_estoque(produto_teste, -10)
            produto = Produto.query.get(produto_teste)
            assert produto.quantidade == estoque_inicial + 10


class TestProdutoModel:
    """Testes para o modelo Produto"""
    
    def test_produto_creation(self, app):
        """Testa criação de produto"""
        with app.app_context():
            produto = Produto(
                nome='Produto Model',
                valor_compra=5.0,
                valor_venda=8.0,
                quantidade=50,
                estoque_minimo=5
            )
            
            db.session.add(produto)
            db.session.commit()
            
            assert produto.id is not None
            assert produto.nome == 'Produto Model'
    
    def test_produto_margem_lucro(self, app):
        """Testa cálculo da margem de lucro"""
        with app.app_context():
            produto = Produto(
                nome='Produto Margem',
                valor_compra=10.0,
                valor_venda=15.0
            )
            
            # Margem = ((15 - 10) / 10) * 100 = 50%
            assert produto.margem_lucro == 50.0
    
    def test_produto_estoque_baixo_property(self, app):
        """Testa propriedade de estoque baixo"""
        with app.app_context():
            produto1 = Produto(
                nome='Produto 1',
                valor_compra=10.0,
                valor_venda=15.0,
                quantidade=5,
                estoque_minimo=10
            )
            
            produto2 = Produto(
                nome='Produto 2',
                valor_compra=10.0,
                valor_venda=15.0,
                quantidade=15,
                estoque_minimo=10
            )
            
            assert produto1.estoque_baixo is True
            assert produto2.estoque_baixo is False
    
    def test_produto_to_dict(self, app):
        """Testa conversão para dicionário"""
        with app.app_context():
            produto = Produto(
                nome='Produto Dict',
                valor_compra=7.0,
                valor_venda=10.0,
                quantidade=25,
                estoque_minimo=5
            )
            
            produto_dict = produto.to_dict()
            
            assert produto_dict['nome'] == 'Produto Dict'
            assert produto_dict['valor_compra'] == 7.0
            assert produto_dict['valor_venda'] == 10.0
            assert produto_dict['quantidade'] == 25
            assert 'margem_lucro' in produto_dict
    
    def test_produto_repr(self, app, produto_teste):
        """Testa representação string do produto"""
        with app.app_context():
            produto = Produto.query.get(produto_teste)
            repr_str = repr(produto)
            assert 'Produto Teste' in repr_str
        assert 'Produto' in repr_str
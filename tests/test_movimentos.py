"""
Testes para o módulo de movimentos de estoque
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Movimento, Produto, db
from app.services.movimento_service import MovimentoService


class TestMovimentosBlueprint:
    """Testes para as rotas de movimentos"""
    
    def test_movimentos_list_requires_auth(self, client):
        """Testa se a listagem de movimentos requer autenticação"""
        response = client.get('/movimentos/')
        assert response.status_code == 302  # Redirect para login
    
    def test_movimentos_list_authenticated(self, authenticated_admin_client, movimento_teste):
        """Testa listagem de movimentos autenticado"""
        response = authenticated_admin_client.get('/movimentos/')
        assert response.status_code == 200
        assert b'Movimento de teste' in response.data
    
    def test_movimentos_list_with_filters(self, authenticated_admin_client, movimento_teste):
        """Testa listagem de movimentos com filtros"""
        hoje = datetime.now().date()
        response = authenticated_admin_client.get(f'/movimentos/?tipo=entrada&data_inicio={hoje}&data_fim={hoje}')
        assert response.status_code == 200
    
    def test_entrada_form_get(self, authenticated_admin_client):
        """Testa acesso ao formulário de entrada"""
        response = authenticated_admin_client.get('/movimentos/entrada')
        assert response.status_code == 200
        assert b'entrada' in response.data.lower()
    
    def test_entrada_success(self, authenticated_admin_client, produto_teste, app):
        """Testa registro de entrada com sucesso"""
        estoque_inicial = produto_teste.quantidade
        
        response = authenticated_admin_client.post('/movimentos/entrada', data={
            'produto_id': str(produto_teste.id),
            'quantidade': '25',
            'valor_unitario': '12.00',
            'observacao': 'Entrada teste'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se o estoque foi atualizado
        with app.app_context():
            produto = Produto.query.get(produto_teste.id)
            assert produto.quantidade == estoque_inicial + 25
            
            # Verifica se o movimento foi registrado
            movimento = Movimento.query.filter_by(
                produto_id=produto_teste.id,
                tipo='entrada',
                observacao='Entrada teste'
            ).first()
            assert movimento is not None
            assert movimento.quantidade == 25
            assert movimento.valor_unitario == 12.00
    
    def test_entrada_without_valor_unitario(self, authenticated_admin_client, produto_teste, app):
        """Testa entrada sem valor unitário (usa valor de compra)"""
        response = authenticated_admin_client.post('/movimentos/entrada', data={
            'produto_id': str(produto_teste.id),
            'quantidade': '10',
            'observacao': 'Entrada sem valor'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        with app.app_context():
            movimento = Movimento.query.filter_by(
                produto_id=produto_teste.id,
                observacao='Entrada sem valor'
            ).first()
            assert movimento is not None
            assert movimento.valor_unitario == produto_teste.valor_compra
    
    def test_entrada_invalid_data(self, authenticated_admin_client, produto_teste):
        """Testa entrada com dados inválidos"""
        response = authenticated_admin_client.post('/movimentos/entrada', data={
            'produto_id': '9999',  # Produto inexistente
            'quantidade': '10',
            'valor_unitario': '12.00'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'erro' in response.data.lower()
    
    def test_saida_form_get(self, authenticated_admin_client):
        """Testa acesso ao formulário de saída"""
        response = authenticated_admin_client.get('/movimentos/saida')
        assert response.status_code == 200
        assert b'sa' in response.data.lower()  # saída
    
    def test_saida_success(self, authenticated_admin_client, produto_teste, app):
        """Testa registro de saída com sucesso"""
        estoque_inicial = produto_teste.quantidade
        
        response = authenticated_admin_client.post('/movimentos/saida', data={
            'produto_id': str(produto_teste.id),
            'quantidade': '15',
            'valor_unitario': '18.00',
            'observacao': 'Saída teste',
            'forma_pagamento': 'dinheiro'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se o estoque foi atualizado
        with app.app_context():
            produto = Produto.query.get(produto_teste.id)
            assert produto.quantidade == estoque_inicial - 15
            
            # Verifica se o movimento foi registrado
            movimento = Movimento.query.filter_by(
                produto_id=produto_teste.id,
                tipo='saida',
                observacao='Saída teste'
            ).first()
            assert movimento is not None
            assert movimento.quantidade == 15
            assert movimento.valor_unitario == 18.00
    
    def test_saida_without_valor_unitario(self, authenticated_admin_client, produto_teste, app):
        """Testa saída sem valor unitário (usa valor de venda)"""
        response = authenticated_admin_client.post('/movimentos/saida', data={
            'produto_id': str(produto_teste.id),
            'quantidade': '5',
            'observacao': 'Saída sem valor',
            'forma_pagamento': 'cartao'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        with app.app_context():
            movimento = Movimento.query.filter_by(
                produto_id=produto_teste.id,
                observacao='Saída sem valor'
            ).first()
            assert movimento is not None
            assert movimento.valor_unitario == produto_teste.valor_venda
    
    def test_saida_estoque_insuficiente(self, authenticated_admin_client, produto_teste):
        """Testa saída com estoque insuficiente"""
        response = authenticated_admin_client.post('/movimentos/saida', data={
            'produto_id': str(produto_teste.id),
            'quantidade': str(produto_teste.quantidade + 1),  # Mais que o estoque
            'forma_pagamento': 'dinheiro'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'erro' in response.data.lower() or b'insuficiente' in response.data.lower()


class TestMovimentoService:
    """Testes para o serviço de movimentos"""
    
    def test_listar_movimentos_todos(self, app, movimento_teste):
        """Testa listagem de todos os movimentos"""
        with app.app_context():
            movimentos = MovimentoService.listar_movimentos()
            assert len(movimentos) >= 1
            assert any(m.observacao == 'Movimento de teste' for m in movimentos)
    
    def test_listar_movimentos_por_produto(self, app, movimento_teste, produto_teste):
        """Testa listagem de movimentos por produto"""
        with app.app_context():
            movimentos = MovimentoService.listar_movimentos(produto_id=produto_teste.id)
            assert len(movimentos) >= 1
            assert all(m.produto_id == produto_teste.id for m in movimentos)
    
    def test_listar_movimentos_por_tipo(self, app, movimento_teste):
        """Testa listagem de movimentos por tipo"""
        with app.app_context():
            movimentos = MovimentoService.listar_movimentos(tipo='entrada')
            assert all(m.tipo == 'entrada' for m in movimentos)
    
    def test_listar_movimentos_por_periodo(self, app):
        """Testa listagem de movimentos por período"""
        with app.app_context():
            hoje = datetime.now().date()
            ontem = hoje - timedelta(days=1)
            
            movimentos = MovimentoService.listar_movimentos(
                data_inicio=datetime.combine(ontem, datetime.min.time()),
                data_fim=datetime.combine(hoje, datetime.max.time())
            )
            
            for movimento in movimentos:
                assert ontem <= movimento.data_movimento.date() <= hoje
    
    def test_registrar_entrada(self, app, produto_teste):
        """Testa registro de entrada"""
        with app.app_context():
            estoque_inicial = produto_teste.quantidade
            
            movimento = MovimentoService.registrar_entrada(
                produto_id=produto_teste.id,
                quantidade=30,
                valor_unitario=11.0,
                observacao='Entrada service'
            )
            
            assert movimento.tipo == 'entrada'
            assert movimento.quantidade == 30
            assert movimento.valor_unitario == 11.0
            assert movimento.valor_total == 330.0
            
            # Verifica atualização do estoque
            produto = Produto.query.get(produto_teste.id)
            assert produto.quantidade == estoque_inicial + 30
    
    def test_registrar_entrada_sem_valor(self, app, produto_teste):
        """Testa registro de entrada sem valor unitário"""
        with app.app_context():
            movimento = MovimentoService.registrar_entrada(
                produto_id=produto_teste.id,
                quantidade=20,
                observacao='Entrada sem valor'
            )
            
            assert movimento.valor_unitario == produto_teste.valor_compra
            assert movimento.valor_total == 20 * produto_teste.valor_compra
    
    def test_registrar_saida(self, app, produto_teste):
        """Testa registro de saída"""
        with app.app_context():
            estoque_inicial = produto_teste.quantidade
            
            movimento = MovimentoService.registrar_saida(
                produto_id=produto_teste.id,
                quantidade=20,
                valor_unitario=16.0,
                observacao='Saída service'
            )
            
            assert movimento.tipo == 'saida'
            assert movimento.quantidade == 20
            assert movimento.valor_unitario == 16.0
            assert movimento.valor_total == 320.0
            
            # Verifica atualização do estoque
            produto = Produto.query.get(produto_teste.id)
            assert produto.quantidade == estoque_inicial - 20
    
    def test_registrar_saida_estoque_insuficiente(self, app, produto_teste):
        """Testa registro de saída com estoque insuficiente"""
        with app.app_context():
            with pytest.raises(Exception) as excinfo:
                MovimentoService.registrar_saida(
                    produto_id=produto_teste.id,
                    quantidade=produto_teste.quantidade + 1,
                    valor_unitario=15.0
                )
            
            assert 'estoque' in str(excinfo.value).lower()
    
    def test_obter_movimento(self, app, movimento_teste):
        """Testa obter movimento por ID"""
        with app.app_context():
            movimento = MovimentoService.obter_movimento(movimento_teste.id)
            assert movimento is not None
            assert movimento.observacao == 'Movimento de teste'
    
    def test_obter_movimento_inexistente(self, app):
        """Testa obter movimento inexistente"""
        with app.app_context():
            movimento = MovimentoService.obter_movimento(9999)
            assert movimento is None
    
    def test_calcular_resumo_movimentos(self, app, produto_teste):
        """Testa cálculo de resumo dos movimentos"""
        with app.app_context():
            # Registra alguns movimentos
            MovimentoService.registrar_entrada(produto_teste.id, 50, 10.0, 'Entrada 1')
            MovimentoService.registrar_entrada(produto_teste.id, 30, 12.0, 'Entrada 2')
            MovimentoService.registrar_saida(produto_teste.id, 20, 15.0, 'Saída 1')
            
            resumo = MovimentoService.calcular_resumo_movimentos(
                produto_id=produto_teste.id
            )
            
            assert resumo['total_entradas'] == 80
            assert resumo['valor_total_entradas'] == 860.0  # 50*10 + 30*12
            assert resumo['total_saidas'] == 20
            assert resumo['valor_total_saidas'] == 300.0  # 20*15


class TestMovimentoModel:
    """Testes para o modelo Movimento"""
    
    def test_movimento_creation(self, app, produto_teste):
        """Testa criação de movimento"""
        with app.app_context():
            movimento = Movimento(
                produto_id=produto_teste.id,
                tipo='entrada',
                quantidade=25,
                valor_unitario=10.0,
                valor_total=250.0,
                observacao='Movimento model'
            )
            
            db.session.add(movimento)
            db.session.commit()
            
            assert movimento.id is not None
            assert movimento.data_movimento is not None
    
    def test_movimento_calcular_valor_total(self, app, produto_teste):
        """Testa cálculo automático do valor total"""
        with app.app_context():
            movimento = Movimento(
                produto_id=produto_teste.id,
                tipo='saida',
                quantidade=15,
                valor_unitario=12.0
            )
            
            movimento.calcular_valor_total()
            assert movimento.valor_total == 180.0
    
    def test_movimento_to_dict(self, app, produto_teste):
        """Testa conversão para dicionário"""
        with app.app_context():
            movimento = Movimento(
                produto_id=produto_teste.id,
                tipo='entrada',
                quantidade=40,
                valor_unitario=8.0,
                valor_total=320.0,
                observacao='Movimento dict'
            )
            
            db.session.add(movimento)
            db.session.commit()
            
            movimento_dict = movimento.to_dict()
            
            assert movimento_dict['tipo'] == 'entrada'
            assert movimento_dict['quantidade'] == 40
            assert movimento_dict['valor_unitario'] == 8.0
            assert movimento_dict['valor_total'] == 320.0
            assert 'data_movimento' in movimento_dict
    
    def test_movimento_repr(self, movimento_teste):
        """Testa representação string do movimento"""
        repr_str = repr(movimento_teste)
        assert 'Movimento' in repr_str
        assert 'entrada' in repr_str
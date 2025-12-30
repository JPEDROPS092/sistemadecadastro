"""
Testes para o módulo de caixa
"""
import pytest
import sys
import os
from datetime import datetime

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Caixa, MovimentoCaixa, db
from app.services.caixa_service import CaixaService


class TestCaixaBlueprint:
    """Testes para as rotas de caixa"""
    
    def test_caixa_index_requires_auth(self, client):
        """Testa se o caixa requer autenticação"""
        response = client.get('/caixa/')
        assert response.status_code == 302  # Redirect para login
    
    def test_caixa_index_without_caixa_aberto(self, authenticated_admin_client):
        """Testa índice do caixa sem caixa aberto"""
        response = authenticated_admin_client.get('/caixa/')
        assert response.status_code == 200
        assert b'abrir' in response.data.lower() or b'caixa' in response.data.lower()
    
    def test_caixa_index_with_caixa_aberto(self, authenticated_admin_client, caixa_aberto):
        """Testa índice do caixa com caixa aberto"""
        response = authenticated_admin_client.get('/caixa/')
        assert response.status_code == 200
        assert b'fechar' in response.data.lower() or b'moviment' in response.data.lower()
    
    def test_abrir_caixa_success(self, authenticated_admin_client, app):
        """Testa abertura de caixa com sucesso"""
        response = authenticated_admin_client.post('/caixa/abrir', data={
            'saldo_inicial': '150.00',
            'observacao': 'Abertura teste'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se o caixa foi aberto
        with app.app_context():
            caixa = Caixa.query.filter_by(
                data_fechamento=None,
                observacao_abertura='Abertura teste'
            ).first()
            assert caixa is not None
            assert caixa.saldo_inicial == 150.0
            assert caixa.saldo_atual == 150.0
    
    def test_abrir_caixa_com_caixa_ja_aberto(self, authenticated_admin_client, caixa_aberto):
        """Testa abertura de caixa quando já existe um aberto"""
        response = authenticated_admin_client.post('/caixa/abrir', data={
            'saldo_inicial': '100.00'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'erro' in response.data.lower() or b'aberto' in response.data.lower()
    
    def test_fechar_caixa_success(self, authenticated_admin_client, caixa_aberto, app):
        """Testa fechamento de caixa com sucesso"""
        response = authenticated_admin_client.post('/caixa/fechar', data={
            'observacao': 'Fechamento teste'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se o caixa foi fechado
        with app.app_context():
            caixa = Caixa.query.get(caixa_aberto.id)
            assert caixa.data_fechamento is not None
            assert caixa.observacao_fechamento == 'Fechamento teste'
    
    def test_fechar_caixa_sem_caixa_aberto(self, authenticated_admin_client):
        """Testa fechamento de caixa sem caixa aberto"""
        response = authenticated_admin_client.post('/caixa/fechar', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'erro' in response.data.lower() or b'aberto' in response.data.lower()
    
    def test_registrar_movimento_caixa(self, authenticated_admin_client, caixa_aberto, app):
        """Testa registro de movimento no caixa"""
        response = authenticated_admin_client.post('/caixa/movimento', data={
            'tipo': 'saida',
            'categoria': 'despesa',
            'descricao': 'Pagamento fornecedor',
            'valor': '50.00',
            'forma_pagamento': 'dinheiro'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
        
        # Verifica se o movimento foi registrado
        with app.app_context():
            movimento = MovimentoCaixa.query.filter_by(
                caixa_id=caixa_aberto.id,
                descricao='Pagamento fornecedor'
            ).first()
            assert movimento is not None
            assert movimento.tipo == 'saida'
            assert movimento.valor == 50.0
            
            # Verifica se o saldo foi atualizado
            caixa = Caixa.query.get(caixa_aberto.id)
            assert caixa.saldo_atual == caixa_aberto.saldo_inicial - 50.0
    
    def test_registrar_movimento_sem_caixa_aberto(self, authenticated_admin_client):
        """Testa registro de movimento sem caixa aberto"""
        response = authenticated_admin_client.post('/caixa/movimento', data={
            'tipo': 'entrada',
            'categoria': 'receita',
            'descricao': 'Pagamento cliente',
            'valor': '100.00'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'erro' in response.data.lower() or b'aberto' in response.data.lower()
    
    def test_historico_caixas(self, authenticated_admin_client, caixa_aberto):
        """Testa visualização do histórico de caixas"""
        response = authenticated_admin_client.get('/caixa/historico')
        assert response.status_code == 200
        assert b'hist' in response.data.lower() or b'caixa' in response.data.lower()
    
    def test_detalhes_caixa(self, authenticated_admin_client, caixa_aberto):
        """Testa visualização dos detalhes de um caixa"""
        response = authenticated_admin_client.get(f'/caixa/{caixa_aberto.id}')
        assert response.status_code == 200
        assert b'Caixa de teste' in response.data
    
    def test_detalhes_caixa_inexistente(self, authenticated_admin_client):
        """Testa visualização de caixa inexistente"""
        response = authenticated_admin_client.get('/caixa/9999', follow_redirects=True)
        assert response.status_code == 200
        assert b'encontrado' in response.data.lower()


class TestCaixaService:
    """Testes para o serviço de caixa"""
    
    def test_obter_caixa_aberto_existe(self, app, caixa_aberto):
        """Testa obter caixa aberto quando existe"""
        with app.app_context():
            caixa = CaixaService.obter_caixa_aberto()
            assert caixa is not None
            assert caixa.id == caixa_aberto.id
    
    def test_obter_caixa_aberto_nao_existe(self, app):
        """Testa obter caixa aberto quando não existe"""
        with app.app_context():
            caixa = CaixaService.obter_caixa_aberto()
            assert caixa is None
    
    def test_abrir_caixa(self, app, admin_user):
        """Testa abertura de caixa"""
        with app.app_context():
            caixa = CaixaService.abrir_caixa(
                saldo_inicial=200.0,
                observacao='Caixa service'
            )
            
            assert caixa.saldo_inicial == 200.0
            assert caixa.saldo_atual == 200.0
            assert caixa.observacao_abertura == 'Caixa service'
            assert caixa.data_fechamento is None
    
    def test_abrir_caixa_com_caixa_ja_aberto(self, app, caixa_aberto):
        """Testa abertura de caixa quando já existe um aberto"""
        with app.app_context():
            with pytest.raises(Exception) as excinfo:
                CaixaService.abrir_caixa(100.0)
            
            assert 'aberto' in str(excinfo.value).lower()
    
    def test_fechar_caixa(self, app, caixa_aberto):
        """Testa fechamento de caixa"""
        with app.app_context():
            caixa_fechado = CaixaService.fechar_caixa(
                caixa_aberto.id,
                observacao='Fechamento service'
            )
            
            assert caixa_fechado.data_fechamento is not None
            assert caixa_fechado.observacao_fechamento == 'Fechamento service'
    
    def test_fechar_caixa_inexistente(self, app):
        """Testa fechamento de caixa inexistente"""
        with app.app_context():
            with pytest.raises(Exception):
                CaixaService.fechar_caixa(9999)
    
    def test_registrar_movimento_entrada(self, app, caixa_aberto):
        """Testa registro de movimento de entrada"""
        with app.app_context():
            saldo_inicial = caixa_aberto.saldo_atual
            
            movimento = CaixaService.registrar_movimento(
                caixa_id=caixa_aberto.id,
                tipo='entrada',
                categoria='receita',
                descricao='Venda produto',
                valor=75.0,
                forma_pagamento='cartao'
            )
            
            assert movimento.tipo == 'entrada'
            assert movimento.valor == 75.0
            assert movimento.categoria == 'receita'
            
            # Verifica atualização do saldo
            caixa = Caixa.query.get(caixa_aberto.id)
            assert caixa.saldo_atual == saldo_inicial + 75.0
    
    def test_registrar_movimento_saida(self, app, caixa_aberto):
        """Testa registro de movimento de saída"""
        with app.app_context():
            saldo_inicial = caixa_aberto.saldo_atual
            
            movimento = CaixaService.registrar_movimento(
                caixa_id=caixa_aberto.id,
                tipo='saida',
                categoria='despesa',
                descricao='Pagamento aluguel',
                valor=300.0,
                forma_pagamento='transferencia'
            )
            
            assert movimento.tipo == 'saida'
            assert movimento.valor == 300.0
            
            # Verifica atualização do saldo
            caixa = Caixa.query.get(caixa_aberto.id)
            assert caixa.saldo_atual == saldo_inicial - 300.0
    
    def test_registrar_movimento_saldo_insuficiente(self, app, caixa_aberto):
        """Testa registro de movimento com saldo insuficiente"""
        with app.app_context():
            with pytest.raises(Exception) as excinfo:
                CaixaService.registrar_movimento(
                    caixa_id=caixa_aberto.id,
                    tipo='saida',
                    categoria='despesa',
                    descricao='Gasto maior que saldo',
                    valor=caixa_aberto.saldo_atual + 1,
                    forma_pagamento='dinheiro'
                )
            
            assert 'saldo' in str(excinfo.value).lower()
    
    def test_listar_caixas(self, app, caixa_aberto):
        """Testa listagem de caixas"""
        with app.app_context():
            caixas = CaixaService.listar_caixas()
            assert len(caixas) >= 1
            assert any(c.id == caixa_aberto.id for c in caixas)
    
    def test_obter_caixa_por_id(self, app, caixa_aberto):
        """Testa obter caixa por ID"""
        with app.app_context():
            caixa = CaixaService.obter_caixa(caixa_aberto.id)
            assert caixa is not None
            assert caixa.id == caixa_aberto.id
    
    def test_obter_caixa_inexistente(self, app):
        """Testa obter caixa inexistente"""
        with app.app_context():
            caixa = CaixaService.obter_caixa(9999)
            assert caixa is None
    
    def test_listar_movimentos_caixa(self, app, caixa_aberto):
        """Testa listagem de movimentos do caixa"""
        with app.app_context():
            # Registra alguns movimentos
            CaixaService.registrar_movimento(
                caixa_aberto.id, 'entrada', 'receita', 'Receita 1', 100.0
            )
            CaixaService.registrar_movimento(
                caixa_aberto.id, 'saida', 'despesa', 'Despesa 1', 50.0
            )
            
            movimentos = CaixaService.listar_movimentos_caixa(caixa_aberto.id)
            assert len(movimentos) == 2
            
            descricoes = [m.descricao for m in movimentos]
            assert 'Receita 1' in descricoes
            assert 'Despesa 1' in descricoes
    
    def test_calcular_resumo_caixa(self, app, caixa_aberto):
        """Testa cálculo de resumo do caixa"""
        with app.app_context():
            # Registra movimentos
            CaixaService.registrar_movimento(
                caixa_aberto.id, 'entrada', 'receita', 'Receita 1', 200.0
            )
            CaixaService.registrar_movimento(
                caixa_aberto.id, 'entrada', 'receita', 'Receita 2', 150.0
            )
            CaixaService.registrar_movimento(
                caixa_aberto.id, 'saida', 'despesa', 'Despesa 1', 75.0
            )
            
            resumo = CaixaService.calcular_resumo_caixa(caixa_aberto.id)
            
            assert resumo['total_entradas'] == 350.0
            assert resumo['total_saidas'] == 75.0
            assert resumo['saldo_inicial'] == caixa_aberto.saldo_inicial
            assert resumo['saldo_final'] == caixa_aberto.saldo_inicial + 275.0


class TestCaixaModel:
    """Testes para o modelo Caixa"""
    
    def test_caixa_creation(self, app, admin_user):
        """Testa criação de caixa"""
        with app.app_context():
            caixa = Caixa(
                data_abertura=datetime.now(),
                saldo_inicial=250.0,
                saldo_atual=250.0,
                usuario_abertura_id=admin_user.id,
                observacao_abertura='Caixa model'
            )
            
            db.session.add(caixa)
            db.session.commit()
            
            assert caixa.id is not None
            assert caixa.saldo_inicial == 250.0
    
    def test_caixa_is_aberto(self, app, caixa_aberto):
        """Testa propriedade is_aberto"""
        assert caixa_aberto.is_aberto is True
        
        # Fecha o caixa
        with app.app_context():
            caixa_aberto.data_fechamento = datetime.now()
            db.session.commit()
            
            assert caixa_aberto.is_aberto is False
    
    def test_caixa_to_dict(self, app, caixa_aberto):
        """Testa conversão para dicionário"""
        caixa_dict = caixa_aberto.to_dict()
        
        assert caixa_dict['saldo_inicial'] == 100.0
        assert caixa_dict['saldo_atual'] == 100.0
        assert caixa_dict['observacao_abertura'] == 'Caixa de teste'
        assert 'data_abertura' in caixa_dict
    
    def test_caixa_repr(self, caixa_aberto):
        """Testa representação string do caixa"""
        repr_str = repr(caixa_aberto)
        assert 'Caixa' in repr_str
        assert str(caixa_aberto.id) in repr_str


class TestMovimentoCaixaModel:
    """Testes para o modelo MovimentoCaixa"""
    
    def test_movimento_caixa_creation(self, app, caixa_aberto):
        """Testa criação de movimento de caixa"""
        with app.app_context():
            movimento = MovimentoCaixa(
                caixa_id=caixa_aberto.id,
                tipo='entrada',
                categoria='receita',
                descricao='Movimento caixa model',
                valor=125.0,
                forma_pagamento='pix'
            )
            
            db.session.add(movimento)
            db.session.commit()
            
            assert movimento.id is not None
            assert movimento.data_movimento is not None
    
    def test_movimento_caixa_to_dict(self, app, caixa_aberto):
        """Testa conversão para dicionário"""
        with app.app_context():
            movimento = MovimentoCaixa(
                caixa_id=caixa_aberto.id,
                tipo='saida',
                categoria='despesa',
                descricao='Movimento dict',
                valor=80.0,
                forma_pagamento='dinheiro'
            )
            
            db.session.add(movimento)
            db.session.commit()
            
            movimento_dict = movimento.to_dict()
            
            assert movimento_dict['tipo'] == 'saida'
            assert movimento_dict['valor'] == 80.0
            assert movimento_dict['descricao'] == 'Movimento dict'
            assert 'data_movimento' in movimento_dict
    
    def test_movimento_caixa_repr(self, app, caixa_aberto):
        """Testa representação string do movimento de caixa"""
        with app.app_context():
            movimento = MovimentoCaixa(
                caixa_id=caixa_aberto.id,
                tipo='entrada',
                categoria='receita',
                descricao='Movimento repr',
                valor=60.0
            )
            
            repr_str = repr(movimento)
            assert 'MovimentoCaixa' in repr_str
            assert 'entrada' in repr_str
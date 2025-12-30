"""
Testes de integração para o fluxo completo da aplicação
"""
import pytest
import sys
import os
from datetime import datetime

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Usuario, Produto, Movimento, Caixa, MovimentoCaixa, db


class TestFluxoCompletoVenda:
    """Testa o fluxo completo de uma venda"""
    
    def test_fluxo_venda_completa(self, authenticated_admin_client, app):
        """Testa fluxo completo: produto -> estoque -> venda -> caixa"""
        
        # 1. Criar produto
        response = authenticated_admin_client.post('/produtos/novo', data={
            'nome': 'Produto Fluxo',
            'valor_compra': '10.00',
            'valor_venda': '15.00',
            'quantidade': '100',
            'estoque_minimo': '10'
        }, follow_redirects=True)
        assert b'sucesso' in response.data.lower()
        
        with app.app_context():
            produto = Produto.query.filter_by(nome='Produto Fluxo').first()
            assert produto is not None
            produto_id = produto.id
        
        # 2. Abrir caixa
        response = authenticated_admin_client.post('/caixa/abrir', data={
            'saldo_inicial': '200.00',
            'observacao': 'Caixa fluxo teste'
        }, follow_redirects=True)
        assert b'sucesso' in response.data.lower()
        
        with app.app_context():
            caixa = Caixa.query.filter_by(data_fechamento=None).first()
            assert caixa is not None
            assert caixa.saldo_inicial == 200.0
        
        # 3. Registrar entrada de estoque
        response = authenticated_admin_client.post('/movimentos/entrada', data={
            'produto_id': str(produto_id),
            'quantidade': '50',
            'valor_unitario': '10.00',
            'observacao': 'Entrada fluxo'
        }, follow_redirects=True)
        assert b'sucesso' in response.data.lower()
        
        with app.app_context():
            produto = Produto.query.get(produto_id)
            assert produto.quantidade == 150  # 100 inicial + 50 entrada
        
        # 4. Registrar venda
        response = authenticated_admin_client.post('/movimentos/saida', data={
            'produto_id': str(produto_id),
            'quantidade': '20',
            'valor_unitario': '15.00',
            'observacao': 'Venda fluxo',
            'forma_pagamento': 'dinheiro'
        }, follow_redirects=True)
        assert b'sucesso' in response.data.lower()
        
        # 5. Verificar resultados finais
        with app.app_context():
            # Verificar estoque
            produto = Produto.query.get(produto_id)
            assert produto.quantidade == 130  # 150 - 20
            
            # Verificar movimento de saída
            movimento_saida = Movimento.query.filter_by(
                produto_id=produto_id,
                tipo='saida',
                observacao='Venda fluxo'
            ).first()
            assert movimento_saida is not None
            assert movimento_saida.quantidade == 20
            assert movimento_saida.valor_total == 300.0
            
            # Verificar caixa atualizado
            caixa = Caixa.query.filter_by(data_fechamento=None).first()
            assert caixa.saldo_atual == 500.0  # 200 + 300 da venda
            
            # Verificar movimento no caixa
            movimento_caixa = MovimentoCaixa.query.filter_by(
                caixa_id=caixa.id,
                tipo='entrada'
            ).first()
            assert movimento_caixa is not None
            assert movimento_caixa.valor == 300.0
        
        # 6. Fechar caixa
        response = authenticated_admin_client.post('/caixa/fechar', data={
            'observacao': 'Fechamento fluxo'
        }, follow_redirects=True)
        assert b'sucesso' in response.data.lower()
        
        with app.app_context():
            caixa = Caixa.query.get(caixa.id)
            assert caixa.data_fechamento is not None
    
    def test_fluxo_multiplas_vendas(self, authenticated_admin_client, app):
        """Testa fluxo com múltiplas vendas em sequência"""
        
        # Criar produto
        response = authenticated_admin_client.post('/produtos/novo', data={
            'nome': 'Produto Multiplas',
            'valor_compra': '8.00',
            'valor_venda': '12.00',
            'quantidade': '200',
            'estoque_minimo': '20'
        }, follow_redirects=True)
        
        with app.app_context():
            produto = Produto.query.filter_by(nome='Produto Multiplas').first()
            produto_id = produto.id
        
        # Abrir caixa
        authenticated_admin_client.post('/caixa/abrir', data={
            'saldo_inicial': '100.00'
        })
        
        # Realizar múltiplas vendas
        vendas = [
            {'quantidade': '10', 'forma_pagamento': 'dinheiro'},
            {'quantidade': '15', 'forma_pagamento': 'cartao'},
            {'quantidade': '5', 'forma_pagamento': 'pix'}
        ]
        
        for i, venda in enumerate(vendas):
            response = authenticated_admin_client.post('/movimentos/saida', data={
                'produto_id': str(produto_id),
                'quantidade': venda['quantidade'],
                'observacao': f'Venda {i+1}',
                'forma_pagamento': venda['forma_pagamento']
            }, follow_redirects=True)
            assert b'sucesso' in response.data.lower()
        
        # Verificar resultados
        with app.app_context():
            produto = Produto.query.get(produto_id)
            assert produto.quantidade == 170  # 200 - 30
            
            caixa = Caixa.query.filter_by(data_fechamento=None).first()
            # Total vendas: (10 + 15 + 5) * 12 = 360
            assert caixa.saldo_atual == 460.0  # 100 + 360


class TestFluxoGestaoEstoque:
    """Testa fluxos de gestão de estoque"""
    
    def test_fluxo_estoque_baixo_reposicao(self, authenticated_admin_client, app):
        """Testa fluxo: estoque baixo -> alerta -> reposição"""
        
        # Criar produto com estoque baixo
        response = authenticated_admin_client.post('/produtos/novo', data={
            'nome': 'Produto Estoque Baixo',
            'valor_compra': '5.00',
            'valor_venda': '8.00',
            'quantidade': '5',  # Abaixo do mínimo
            'estoque_minimo': '20'
        }, follow_redirects=True)
        
        with app.app_context():
            produto = Produto.query.filter_by(nome='Produto Estoque Baixo').first()
            produto_id = produto.id
            assert produto.estoque_baixo is True
        
        # Verificar na listagem de estoque baixo
        response = authenticated_admin_client.get('/produtos/estoque-baixo')
        assert b'Produto Estoque Baixo' in response.data
        
        # Fazer reposição
        response = authenticated_admin_client.post('/movimentos/entrada', data={
            'produto_id': str(produto_id),
            'quantidade': '50',
            'valor_unitario': '5.00',
            'observacao': 'Reposição estoque'
        }, follow_redirects=True)
        assert b'sucesso' in response.data.lower()
        
        # Verificar que não está mais em estoque baixo
        with app.app_context():
            produto = Produto.query.get(produto_id)
            assert produto.quantidade == 55
            assert produto.estoque_baixo is False
        
        response = authenticated_admin_client.get('/produtos/estoque-baixo')
        assert b'Produto Estoque Baixo' not in response.data
    
    def test_fluxo_controle_estoque_vendas(self, authenticated_admin_client, app):
        """Testa controle de estoque durante vendas"""
        
        # Criar produto com estoque limitado
        response = authenticated_admin_client.post('/produtos/novo', data={
            'nome': 'Produto Limitado',
            'valor_compra': '10.00',
            'valor_venda': '15.00',
            'quantidade': '10',
            'estoque_minimo': '5'
        })
        
        with app.app_context():
            produto = Produto.query.filter_by(nome='Produto Limitado').first()
            produto_id = produto.id
        
        # Tentar vender mais do que tem em estoque
        response = authenticated_admin_client.post('/movimentos/saida', data={
            'produto_id': str(produto_id),
            'quantidade': '15',  # Mais que os 10 disponíveis
            'observacao': 'Venda impossível'
        }, follow_redirects=True)
        assert b'erro' in response.data.lower() or b'insuficiente' in response.data.lower()
        
        # Venda válida
        response = authenticated_admin_client.post('/movimentos/saida', data={
            'produto_id': str(produto_id),
            'quantidade': '8',
            'observacao': 'Venda válida'
        }, follow_redirects=True)
        assert b'sucesso' in response.data.lower()
        
        # Verificar estoque restante
        with app.app_context():
            produto = Produto.query.get(produto_id)
            assert produto.quantidade == 2
            assert produto.estoque_baixo is True  # Abaixo do mínimo (5)


class TestFluxoCaixaDiario:
    """Testa fluxo completo de caixa diário"""
    
    def test_fluxo_caixa_operacao_diaria(self, authenticated_admin_client, app):
        """Testa operação completa de caixa em um dia"""
        
        # Abrir caixa
        response = authenticated_admin_client.post('/caixa/abrir', data={
            'saldo_inicial': '500.00',
            'observacao': 'Abertura dia teste'
        })
        
        with app.app_context():
            caixa = Caixa.query.filter_by(data_fechamento=None).first()
            caixa_id = caixa.id
        
        # Registrar várias operações
        operacoes = [
            {'tipo': 'entrada', 'categoria': 'receita', 'descricao': 'Venda produto A', 'valor': '100.00', 'forma_pagamento': 'dinheiro'},
            {'tipo': 'entrada', 'categoria': 'receita', 'descricao': 'Venda produto B', 'valor': '75.00', 'forma_pagamento': 'cartao'},
            {'tipo': 'saida', 'categoria': 'despesa', 'descricao': 'Compra material', 'valor': '30.00', 'forma_pagamento': 'dinheiro'},
            {'tipo': 'saida', 'categoria': 'despesa', 'descricao': 'Pagamento conta', 'valor': '45.00', 'forma_pagamento': 'transferencia'},
            {'tipo': 'entrada', 'categoria': 'receita', 'descricao': 'Venda produto C', 'valor': '120.00', 'forma_pagamento': 'pix'}
        ]
        
        for operacao in operacoes:
            response = authenticated_admin_client.post('/caixa/movimento', data=operacao, follow_redirects=True)
            assert b'sucesso' in response.data.lower()
        
        # Verificar saldo final
        with app.app_context():
            caixa = Caixa.query.get(caixa_id)
            # Saldo final = 500 + 100 + 75 - 30 - 45 + 120 = 720
            assert caixa.saldo_atual == 720.0
            
            # Verificar movimentos registrados
            movimentos = MovimentoCaixa.query.filter_by(caixa_id=caixa_id).all()
            assert len(movimentos) == 5
            
            entradas = [m for m in movimentos if m.tipo == 'entrada']
            saidas = [m for m in movimentos if m.tipo == 'saida']
            
            assert len(entradas) == 3
            assert len(saidas) == 2
            
            total_entradas = sum(m.valor for m in entradas)
            total_saidas = sum(m.valor for m in saidas)
            
            assert total_entradas == 295.0  # 100 + 75 + 120
            assert total_saidas == 75.0     # 30 + 45
        
        # Fechar caixa e verificar relatório
        response = authenticated_admin_client.post('/caixa/fechar', data={
            'observacao': 'Fechamento dia teste'
        })
        
        with app.app_context():
            caixa = Caixa.query.get(caixa_id)
            assert caixa.data_fechamento is not None
        
        # Verificar detalhes do caixa fechado
        response = authenticated_admin_client.get(f'/caixa/{caixa_id}')
        assert response.status_code == 200
        assert b'720' in response.data  # Saldo final
        assert b'295' in response.data  # Total entradas
        assert b'75' in response.data   # Total saídas


class TestFluxoRelatorios:
    """Testa fluxo de geração de relatórios"""
    
    def test_fluxo_relatorios_completos(self, authenticated_admin_client, app):
        """Testa geração de todos os relatórios com dados"""
        
        # Preparar dados de teste
        with app.app_context():
            # Criar produtos
            from app.services.produto_service import ProdutoService
            from app.services.movimento_service import MovimentoService
            from app.services.caixa_service import CaixaService
            
            produto1 = ProdutoService.criar_produto('Produto Rel 1', 10.0, 15.0, 100, 10)
            produto2 = ProdutoService.criar_produto('Produto Rel 2', 8.0, 12.0, 50, 5)
            
            # Abrir caixa
            caixa = CaixaService.abrir_caixa(300.0, 'Caixa relatórios')
            
            # Registrar movimentos
            MovimentoService.registrar_entrada(produto1.id, 20, 10.0, 'Entrada rel 1')
            MovimentoService.registrar_saida(produto1.id, 30, 15.0, 'Venda rel 1')
            MovimentoService.registrar_saida(produto2.id, 15, 12.0, 'Venda rel 2')
            
            # Registrar movimentos no caixa
            CaixaService.registrar_movimento(caixa.id, 'entrada', 'receita', 'Venda 1', 450.0, 'cartao')
            CaixaService.registrar_movimento(caixa.id, 'entrada', 'receita', 'Venda 2', 180.0, 'dinheiro')
            CaixaService.registrar_movimento(caixa.id, 'saida', 'despesa', 'Despesa', 100.0, 'dinheiro')
        
        # Testar dashboard
        response = authenticated_admin_client.get('/')
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower() or b'painel' in response.data.lower()
        
        # Testar relatório de estoque
        response = authenticated_admin_client.get('/relatorios/estoque')
        assert response.status_code == 200
        assert b'Produto Rel 1' in response.data
        assert b'Produto Rel 2' in response.data
        
        # Testar relatório de movimentos
        response = authenticated_admin_client.get('/relatorios/movimentos?periodo=dia')
        assert response.status_code == 200
        assert b'moviment' in response.data.lower()
        
        # Testar relatório de caixa
        response = authenticated_admin_client.get('/relatorios/caixa')
        assert response.status_code == 200
        assert b'caixa' in response.data.lower()
        
        # Testar relatório de fluxo diário
        response = authenticated_admin_client.get('/relatorios/fluxo-diario')
        assert response.status_code == 200
        assert b'fluxo' in response.data.lower()


class TestFluxoPermissoes:
    """Testa fluxo de permissões de usuários"""
    
    def test_fluxo_admin_completo(self, authenticated_admin_client):
        """Testa que admin tem acesso a todas as funcionalidades"""
        
        # Admin deve acessar todas as rotas principais
        rotas_admin = [
            '/',
            '/produtos/',
            '/produtos/novo',
            '/movimentos/',
            '/movimentos/entrada',
            '/movimentos/saida',
            '/caixa/',
            '/relatorios/',
            '/relatorios/estoque',
            '/auth/usuarios',
            '/auth/usuarios/novo'
        ]
        
        for rota in rotas_admin:
            response = authenticated_admin_client.get(rota)
            assert response.status_code == 200, f"Admin não conseguiu acessar {rota}"
    
    def test_fluxo_operador_limitado(self, authenticated_operador_client):
        """Testa que operador tem acesso limitado"""
        
        # Operador deve acessar rotas básicas
        rotas_permitidas = [
            '/',
            '/produtos/',
            '/movimentos/',
            '/movimentos/entrada',
            '/movimentos/saida',
            '/caixa/',
            '/relatorios/estoque'
        ]
        
        for rota in rotas_permitidas:
            response = authenticated_operador_client.get(rota)
            assert response.status_code == 200, f"Operador não conseguiu acessar {rota}"
        
        # Operador NÃO deve acessar rotas administrativas
        rotas_proibidas = [
            '/auth/usuarios',
            '/auth/usuarios/novo'
        ]
        
        for rota in rotas_proibidas:
            response = authenticated_operador_client.get(rota, follow_redirects=True)
            # Deve ser redirecionado ou receber erro
            assert b'Acesso negado' in response.data or b'acesso negado' in response.data, \
                f"Operador conseguiu acessar {rota} indevidamente"


class TestFluxoRecuperacaoErros:
    """Testa fluxos de recuperação de erros"""
    
    def test_fluxo_erro_produto_inexistente(self, authenticated_admin_client):
        """Testa tratamento de erro com produto inexistente"""
        
        # Tentar acessar produto que não existe
        response = authenticated_admin_client.get('/produtos/9999/editar', follow_redirects=True)
        assert b'encontrado' in response.data.lower()
        
        # Tentar registrar movimento para produto inexistente
        response = authenticated_admin_client.post('/movimentos/entrada', data={
            'produto_id': '9999',
            'quantidade': '10'
        }, follow_redirects=True)
        assert b'erro' in response.data.lower()
    
    def test_fluxo_erro_dados_invalidos(self, authenticated_admin_client):
        """Testa tratamento de dados inválidos"""
        
        # Produto com dados inválidos
        response = authenticated_admin_client.post('/produtos/novo', data={
            'nome': '',  # Nome vazio
            'valor_compra': 'abc',  # Valor inválido
            'valor_venda': '-10'  # Valor negativo
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Movimento com quantidade negativa
        response = authenticated_admin_client.post('/movimentos/entrada', data={
            'produto_id': '1',
            'quantidade': '-10'  # Quantidade negativa
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_fluxo_sessao_expirada(self, client):
        """Testa comportamento com sessão expirada"""
        
        # Tentar acessar rota protegida sem autenticação
        response = client.get('/produtos/')
        assert response.status_code == 302  # Redirect para login
        
        response = client.get('/caixa/')
        assert response.status_code == 302
        
        response = client.get('/relatorios/')
        assert response.status_code == 302
"""
Testes para o módulo de relatórios
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.relatorio_service import RelatorioService


class TestRelatoriosBlueprint:
    """Testes para as rotas de relatórios"""
    
    def test_relatorios_index_requires_auth(self, client):
        """Testa se os relatórios requerem autenticação"""
        response = client.get('/relatorios/')
        assert response.status_code == 302  # Redirect para login
    
    def test_relatorios_index_authenticated(self, authenticated_admin_client):
        """Testa acesso ao índice de relatórios autenticado"""
        response = authenticated_admin_client.get('/relatorios/')
        assert response.status_code == 200
        assert b'relat' in response.data.lower()
    
    def test_relatorio_estoque(self, authenticated_admin_client, produto_teste):
        """Testa relatório de estoque"""
        response = authenticated_admin_client.get('/relatorios/estoque')
        assert response.status_code == 200
        assert b'estoque' in response.data.lower()
        assert b'Produto Teste' in response.data
    
    def test_relatorio_movimentos_diario(self, authenticated_admin_client):
        """Testa relatório de movimentos diário"""
        response = authenticated_admin_client.get('/relatorios/movimentos?periodo=dia')
        assert response.status_code == 200
        assert b'moviment' in response.data.lower()
    
    def test_relatorio_movimentos_semanal(self, authenticated_admin_client):
        """Testa relatório de movimentos semanal"""
        response = authenticated_admin_client.get('/relatorios/movimentos?periodo=semana')
        assert response.status_code == 200
        assert b'moviment' in response.data.lower()
    
    def test_relatorio_movimentos_mensal(self, authenticated_admin_client):
        """Testa relatório de movimentos mensal"""
        response = authenticated_admin_client.get('/relatorios/movimentos?periodo=mes')
        assert response.status_code == 200
        assert b'moviment' in response.data.lower()
    
    def test_relatorio_movimentos_periodo_personalizado(self, authenticated_admin_client):
        """Testa relatório de movimentos com período personalizado"""
        hoje = datetime.now().date()
        ontem = hoje - timedelta(days=1)
        
        response = authenticated_admin_client.get(
            f'/relatorios/movimentos?periodo=personalizado'
            f'&data_inicio={ontem}&data_fim={hoje}'
        )
        assert response.status_code == 200
        assert b'moviment' in response.data.lower()
    
    def test_relatorio_fluxo_diario(self, authenticated_admin_client):
        """Testa relatório de fluxo diário"""
        response = authenticated_admin_client.get('/relatorios/fluxo-diario')
        assert response.status_code == 200
        assert b'fluxo' in response.data.lower() or b'di' in response.data.lower()
    
    def test_relatorio_caixa_geral(self, authenticated_admin_client):
        """Testa relatório geral de caixa"""
        response = authenticated_admin_client.get('/relatorios/caixa')
        assert response.status_code == 200
        assert b'caixa' in response.data.lower()
    
    def test_relatorio_caixa_especifico(self, authenticated_admin_client, caixa_aberto):
        """Testa relatório de caixa específico"""
        response = authenticated_admin_client.get(f'/relatorios/caixa?caixa_id={caixa_aberto.id}')
        assert response.status_code == 200
        assert b'caixa' in response.data.lower()


class TestRelatorioService:
    """Testes para o serviço de relatórios"""
    
    def test_dashboard(self, app, produto_teste, movimento_teste):
        """Testa geração do dashboard"""
        with app.app_context():
            dashboard = RelatorioService.dashboard()
            
            assert 'total_produtos' in dashboard
            assert 'produtos_estoque_baixo' in dashboard
            assert 'valor_total_estoque' in dashboard
            assert 'movimentos_hoje' in dashboard
            assert 'vendas_hoje' in dashboard
            assert 'receita_hoje' in dashboard
            
            assert dashboard['total_produtos'] >= 1
    
    def test_relatorio_estoque(self, app, produto_teste):
        """Testa relatório de estoque"""
        with app.app_context():
            relatorio = RelatorioService.relatorio_estoque()
            
            assert 'produtos' in relatorio
            assert 'resumo' in relatorio
            
            produtos = relatorio['produtos']
            assert len(produtos) >= 1
            assert any(p['nome'] == 'Produto Teste' for p in produtos)
            
            resumo = relatorio['resumo']
            assert 'total_produtos' in resumo
            assert 'valor_total_estoque' in resumo
            assert 'produtos_estoque_baixo' in resumo
    
    def test_relatorio_diario(self, app, produto_teste, movimento_teste):
        """Testa relatório diário"""
        with app.app_context():
            relatorio = RelatorioService.relatorio_diario()
            
            assert 'movimentos' in relatorio
            assert 'resumo' in relatorio
            assert 'periodo' in relatorio
            
            resumo = relatorio['resumo']
            assert 'total_entradas' in resumo
            assert 'total_saidas' in resumo
            assert 'valor_total_entradas' in resumo
            assert 'valor_total_saidas' in resumo
    
    def test_relatorio_semanal(self, app):
        """Testa relatório semanal"""
        with app.app_context():
            relatorio = RelatorioService.relatorio_semanal()
            
            assert 'movimentos' in relatorio
            assert 'resumo' in relatorio
            assert 'periodo' in relatorio
            
            # Verifica se o período é de 7 dias
            periodo = relatorio['periodo']
            data_inicio = datetime.fromisoformat(periodo['data_inicio'])
            data_fim = datetime.fromisoformat(periodo['data_fim'])
            diferenca = (data_fim - data_inicio).days
            assert diferenca == 6  # 7 dias incluindo o dia atual
    
    def test_relatorio_mensal(self, app):
        """Testa relatório mensal"""
        with app.app_context():
            relatorio = RelatorioService.relatorio_mensal()
            
            assert 'movimentos' in relatorio
            assert 'resumo' in relatorio
            assert 'periodo' in relatorio
            
            # Verifica se está no mês atual
            periodo = relatorio['periodo']
            data_inicio = datetime.fromisoformat(periodo['data_inicio'])
            assert data_inicio.day == 1  # Primeiro dia do mês
    
    def test_relatorio_movimentos_periodo_personalizado(self, app, produto_teste):
        """Testa relatório de movimentos com período personalizado"""
        with app.app_context():
            hoje = datetime.now()
            ontem = hoje - timedelta(days=1)
            
            relatorio = RelatorioService.relatorio_movimentos(ontem, hoje)
            
            assert 'movimentos' in relatorio
            assert 'resumo' in relatorio
            assert 'periodo' in relatorio
            
            periodo = relatorio['periodo']
            assert periodo['data_inicio'] == ontem.date().isoformat()
            assert periodo['data_fim'] == hoje.date().isoformat()
    
    def test_relatorio_fluxo_diario(self, app, caixa_aberto):
        """Testa relatório de fluxo diário"""
        with app.app_context():
            # Registra alguns movimentos no caixa
            from app.services.caixa_service import CaixaService
            CaixaService.registrar_movimento(
                caixa_aberto.id, 'entrada', 'receita', 'Receita teste', 100.0
            )
            CaixaService.registrar_movimento(
                caixa_aberto.id, 'saida', 'despesa', 'Despesa teste', 30.0
            )
            
            relatorio = RelatorioService.relatorio_fluxo_diario()
            
            assert 'fluxo_por_dia' in relatorio
            assert 'resumo' in relatorio
            
            resumo = relatorio['resumo']
            assert 'total_entradas' in resumo
            assert 'total_saidas' in resumo
            assert 'saldo_liquido' in resumo
    
    def test_relatorio_caixa_geral(self, app, caixa_aberto):
        """Testa relatório geral de caixa"""
        with app.app_context():
            relatorio = RelatorioService.relatorio_caixa()
            
            assert 'caixas' in relatorio
            assert 'resumo_geral' in relatorio
            
            caixas = relatorio['caixas']
            assert len(caixas) >= 1
            assert any(c['id'] == caixa_aberto.id for c in caixas)
    
    def test_relatorio_caixa_especifico(self, app, caixa_aberto):
        """Testa relatório de caixa específico"""
        with app.app_context():
            # Registra movimentos no caixa
            from app.services.caixa_service import CaixaService
            CaixaService.registrar_movimento(
                caixa_aberto.id, 'entrada', 'receita', 'Receita', 200.0
            )
            CaixaService.registrar_movimento(
                caixa_aberto.id, 'saida', 'despesa', 'Despesa', 50.0
            )
            
            relatorio = RelatorioService.relatorio_caixa(caixa_aberto.id)
            
            assert 'caixa' in relatorio
            assert 'movimentos' in relatorio
            assert 'resumo' in relatorio
            
            caixa_info = relatorio['caixa']
            assert caixa_info['id'] == caixa_aberto.id
            
            resumo = relatorio['resumo']
            assert resumo['total_entradas'] == 200.0
            assert resumo['total_saidas'] == 50.0
            assert resumo['saldo_final'] == caixa_aberto.saldo_inicial + 150.0
    
    def test_calcular_vendas_periodo(self, app, produto_teste):
        """Testa cálculo de vendas por período"""
        with app.app_context():
            # Registra algumas vendas (saídas)
            from app.services.movimento_service import MovimentoService
            MovimentoService.registrar_saida(produto_teste.id, 10, 15.0, 'Venda 1')
            MovimentoService.registrar_saida(produto_teste.id, 5, 15.0, 'Venda 2')
            
            hoje = datetime.now().date()
            vendas = RelatorioService.calcular_vendas_periodo(hoje, hoje)
            
            assert vendas['quantidade_total'] == 15
            assert vendas['valor_total'] == 225.0  # 15 * 15.0
            assert vendas['numero_vendas'] == 2
    
    def test_calcular_lucro_periodo(self, app, produto_teste):
        """Testa cálculo de lucro por período"""
        with app.app_context():
            # Registra venda com lucro conhecido
            from app.services.movimento_service import MovimentoService
            MovimentoService.registrar_saida(produto_teste.id, 10, 15.0, 'Venda lucro')
            
            hoje = datetime.now().date()
            lucro = RelatorioService.calcular_lucro_periodo(hoje, hoje)
            
            # Lucro = (valor_venda - valor_compra) * quantidade
            # Lucro = (15.0 - 10.0) * 10 = 50.0
            assert lucro['lucro_total'] == 50.0
            assert lucro['margem_media'] > 0
    
    def test_produtos_mais_vendidos(self, app, produto_teste):
        """Testa listagem de produtos mais vendidos"""
        with app.app_context():
            # Registra vendas
            from app.services.movimento_service import MovimentoService
            MovimentoService.registrar_saida(produto_teste.id, 20, 15.0, 'Venda popular')
            
            produtos_vendidos = RelatorioService.produtos_mais_vendidos(limite=10)
            
            assert len(produtos_vendidos) >= 1
            produto_vendido = produtos_vendidos[0]
            assert produto_vendido['produto_id'] == produto_teste.id
            assert produto_vendido['quantidade_vendida'] == 20
            assert produto_vendido['receita_total'] == 300.0
    
    def test_relatorio_com_dados_vazios(self, app):
        """Testa relatórios com dados vazios"""
        with app.app_context():
            # Testa dashboard sem dados
            dashboard = RelatorioService.dashboard()
            assert dashboard['total_produtos'] == 0
            assert dashboard['valor_total_estoque'] == 0.0
            
            # Testa relatório de estoque sem produtos
            relatorio_estoque = RelatorioService.relatorio_estoque()
            assert len(relatorio_estoque['produtos']) == 0
            assert relatorio_estoque['resumo']['total_produtos'] == 0
            
            # Testa relatório diário sem movimentos
            relatorio_diario = RelatorioService.relatorio_diario()
            assert len(relatorio_diario['movimentos']) == 0
            assert relatorio_diario['resumo']['total_entradas'] == 0
    
    def test_performance_relatorios_grandes(self, app):
        """Testa performance dos relatórios com muitos dados"""
        with app.app_context():
            # Cria muitos produtos e movimentos para testar performance
            from app.services.produto_service import ProdutoService
            from app.services.movimento_service import MovimentoService
            
            produtos = []
            for i in range(50):  # Cria 50 produtos
                produto = ProdutoService.criar_produto(
                    nome=f'Produto Performance {i}',
                    valor_compra=10.0 + i,
                    valor_venda=15.0 + i,
                    quantidade=100,
                    estoque_minimo=10
                )
                produtos.append(produto)
                
                # Registra alguns movimentos para cada produto
                MovimentoService.registrar_entrada(produto.id, 50, produto.valor_compra)
                MovimentoService.registrar_saida(produto.id, 20, produto.valor_venda)
            
            # Testa se os relatórios são gerados em tempo razoável
            import time
            
            start_time = time.time()
            dashboard = RelatorioService.dashboard()
            dashboard_time = time.time() - start_time
            
            start_time = time.time()
            relatorio_estoque = RelatorioService.relatorio_estoque()
            estoque_time = time.time() - start_time
            
            start_time = time.time()
            relatorio_diario = RelatorioService.relatorio_diario()
            diario_time = time.time() - start_time
            
            # Verifica se os relatórios foram gerados corretamente
            assert dashboard['total_produtos'] >= 50
            assert len(relatorio_estoque['produtos']) >= 50
            assert len(relatorio_diario['movimentos']) >= 100  # 2 movimentos por produto
            
            # Verifica se o tempo de execução é aceitável (< 2 segundos cada)
            assert dashboard_time < 2.0
            assert estoque_time < 2.0
            assert diario_time < 2.0
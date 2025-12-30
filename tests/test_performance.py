"""
Testes de performance e stress do sistema
"""
import pytest
import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.produto_service import ProdutoService
from app.services.movimento_service import MovimentoService
from app.services.caixa_service import CaixaService


class TestPerformance:
    """Testes de performance do sistema"""
    
    @pytest.mark.slow
    def test_performance_criacao_produtos_massa(self, app):
        """Testa performance na criação de muitos produtos"""
        
        with app.app_context():
            start_time = time.time()
            
            # Criar 1000 produtos
            produtos_criados = []
            for i in range(1000):
                produto = ProdutoService.criar_produto(
                    nome=f'Produto Performance {i}',
                    valor_compra=10.0 + (i % 10),
                    valor_venda=15.0 + (i % 10),
                    quantidade=100 + (i % 50),
                    estoque_minimo=10
                )
                produtos_criados.append(produto)
            
            end_time = time.time()
            tempo_execucao = end_time - start_time
            
            # Deve criar 1000 produtos em menos de 30 segundos
            assert tempo_execucao < 30.0
            assert len(produtos_criados) == 1000
            
            print(f"Criados 1000 produtos em {tempo_execucao:.2f} segundos")
            print(f"Taxa: {1000/tempo_execucao:.2f} produtos/segundo")
    
    @pytest.mark.slow
    def test_performance_movimentos_massa(self, app, produto_teste):
        """Testa performance no registro de muitos movimentos"""
        
        with app.app_context():
            start_time = time.time()
            
            # Registrar 500 movimentos de cada tipo
            for i in range(500):
                # Entrada
                MovimentoService.registrar_entrada(
                    produto_teste.id,
                    quantidade=10,
                    valor_unitario=10.0,
                    observacao=f'Entrada perf {i}'
                )
                
                # Saída (só se tiver estoque)
                if produto_teste.quantidade >= 5:
                    MovimentoService.registrar_saida(
                        produto_teste.id,
                        quantidade=5,
                        valor_unitario=15.0,
                        observacao=f'Saída perf {i}'
                    )
            
            end_time = time.time()
            tempo_execucao = end_time - start_time
            
            # Deve registrar 1000 movimentos em menos de 45 segundos
            assert tempo_execucao < 45.0
            
            print(f"Registrados 1000 movimentos em {tempo_execucao:.2f} segundos")
            print(f"Taxa: {1000/tempo_execucao:.2f} movimentos/segundo")
    
    @pytest.mark.slow
    def test_performance_consulta_relatorios(self, app):
        """Testa performance na geração de relatórios com muitos dados"""
        
        with app.app_context():
            # Preparar dados (100 produtos com movimentos)
            produtos = []
            for i in range(100):
                produto = ProdutoService.criar_produto(
                    nome=f'Produto Rel Perf {i}',
                    valor_compra=8.0 + (i % 5),
                    valor_venda=12.0 + (i % 5),
                    quantidade=100,
                    estoque_minimo=10
                )
                produtos.append(produto)
                
                # 10 movimentos por produto
                for j in range(10):
                    MovimentoService.registrar_entrada(produto.id, 5, produto.valor_compra)
                    MovimentoService.registrar_saida(produto.id, 3, produto.valor_venda)
            
            # Testar performance dos relatórios
            from app.services.relatorio_service import RelatorioService
            
            # Dashboard
            start_time = time.time()
            dashboard = RelatorioService.dashboard()
            dashboard_time = time.time() - start_time
            
            # Relatório de estoque
            start_time = time.time()
            relatorio_estoque = RelatorioService.relatorio_estoque()
            estoque_time = time.time() - start_time
            
            # Relatório diário
            start_time = time.time()
            relatorio_diario = RelatorioService.relatorio_diario()
            diario_time = time.time() - start_time
            
            # Todos os relatórios devem ser gerados em menos de 3 segundos cada
            assert dashboard_time < 3.0
            assert estoque_time < 3.0
            assert diario_time < 3.0
            
            # Verificar se os dados estão corretos
            assert dashboard['total_produtos'] == 100
            assert len(relatorio_estoque['produtos']) == 100
            assert len(relatorio_diario['movimentos']) >= 2000  # 100 produtos * 20 movimentos
            
            print(f"Dashboard gerado em {dashboard_time:.3f}s")
            print(f"Relatório de estoque gerado em {estoque_time:.3f}s") 
            print(f"Relatório diário gerado em {diario_time:.3f}s")


class TestStress:
    """Testes de stress e concorrência"""
    
    @pytest.mark.slow
    def test_stress_movimentos_concorrentes(self, app, produto_teste):
        """Testa movimentos concorrentes no mesmo produto"""
        
        def registrar_movimentos(produto_id, thread_id):
            """Função para registrar movimentos em thread separada"""
            resultados = []
            for i in range(10):
                try:
                    # Alterna entre entrada e saída
                    if i % 2 == 0:
                        movimento = MovimentoService.registrar_entrada(
                            produto_id, 5, 10.0, f'Thread {thread_id} - Entrada {i}'
                        )
                    else:
                        movimento = MovimentoService.registrar_saida(
                            produto_id, 2, 15.0, f'Thread {thread_id} - Saída {i}'
                        )
                    resultados.append(movimento)
                except Exception as e:
                    resultados.append(f"Erro: {str(e)}")
            return resultados
        
        with app.app_context():
            # Executar 5 threads simultâneas
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for thread_id in range(5):
                    future = executor.submit(registrar_movimentos, produto_teste.id, thread_id)
                    futures.append(future)
                
                # Coletar resultados
                all_results = []
                for future in futures:
                    results = future.result()
                    all_results.extend(results)
                
                # Verificar que a maioria dos movimentos foi bem-sucedida
                successful_movements = [r for r in all_results if not isinstance(r, str)]
                failed_movements = [r for r in all_results if isinstance(r, str)]
                
                # Pelo menos 80% dos movimentos devem ser bem-sucedidos
                success_rate = len(successful_movements) / len(all_results)
                assert success_rate >= 0.8
                
                print(f"Taxa de sucesso: {success_rate:.2%}")
                print(f"Movimentos bem-sucedidos: {len(successful_movements)}")
                print(f"Movimentos falharam: {len(failed_movements)}")
    
    @pytest.mark.slow
    def test_stress_caixa_movimentos_concorrentes(self, app, admin_user):
        """Testa movimentos concorrentes no caixa"""
        
        def registrar_movimentos_caixa(caixa_id, thread_id):
            """Registra movimentos no caixa em thread separada"""
            resultados = []
            for i in range(10):
                try:
                    if i % 2 == 0:
                        movimento = CaixaService.registrar_movimento(
                            caixa_id, 'entrada', 'receita', 
                            f'Thread {thread_id} - Receita {i}', 50.0
                        )
                    else:
                        movimento = CaixaService.registrar_movimento(
                            caixa_id, 'saida', 'despesa',
                            f'Thread {thread_id} - Despesa {i}', 20.0
                        )
                    resultados.append(movimento)
                except Exception as e:
                    resultados.append(f"Erro: {str(e)}")
            return resultados
        
        with app.app_context():
            # Abrir caixa com saldo alto para suportar os testes
            caixa = CaixaService.abrir_caixa(5000.0, 'Caixa stress test')
            
            # Executar 3 threads simultâneas (menos que produtos para evitar conflitos de saldo)
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for thread_id in range(3):
                    future = executor.submit(registrar_movimentos_caixa, caixa.id, thread_id)
                    futures.append(future)
                
                # Coletar resultados
                all_results = []
                for future in futures:
                    results = future.result()
                    all_results.extend(results)
                
                successful_movements = [r for r in all_results if not isinstance(r, str)]
                failed_movements = [r for r in all_results if isinstance(r, str)]
                
                # Pelo menos 90% dos movimentos de caixa devem ser bem-sucedidos
                success_rate = len(successful_movements) / len(all_results)
                assert success_rate >= 0.9
                
                print(f"Taxa de sucesso caixa: {success_rate:.2%}")
                print(f"Movimentos caixa bem-sucedidos: {len(successful_movements)}")
    
    @pytest.mark.slow  
    def test_stress_consultas_simultaneas(self, app):
        """Testa múltiplas consultas simultâneas"""
        
        def executar_consultas():
            """Executa várias consultas em thread separada"""
            resultados = []
            try:
                from app.services.relatorio_service import RelatorioService
                from app.services.produto_service import ProdutoService
                
                # Dashboard
                dashboard = RelatorioService.dashboard()
                resultados.append(('dashboard', len(str(dashboard))))
                
                # Lista produtos
                produtos = ProdutoService.listar_produtos()
                resultados.append(('produtos', len(produtos)))
                
                # Relatório estoque
                rel_estoque = RelatorioService.relatorio_estoque()
                resultados.append(('rel_estoque', len(rel_estoque['produtos'])))
                
                # Relatório diário
                rel_diario = RelatorioService.relatorio_diario()
                resultados.append(('rel_diario', len(rel_diario['movimentos'])))
                
            except Exception as e:
                resultados.append(('erro', str(e)))
            
            return resultados
        
        with app.app_context():
            # Preparar alguns dados
            for i in range(20):
                produto = ProdutoService.criar_produto(
                    f'Produto Stress {i}', 10.0, 15.0, 50
                )
                MovimentoService.registrar_entrada(produto.id, 10, 10.0)
                MovimentoService.registrar_saida(produto.id, 5, 15.0)
            
            # Executar 10 threads fazendo consultas simultaneamente
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(executar_consultas) for _ in range(10)]
                
                all_results = []
                for future in futures:
                    results = future.result()
                    all_results.extend(results)
                
                # Verificar que não houve erros
                errors = [r for r in all_results if r[0] == 'erro']
                assert len(errors) == 0, f"Erros encontrados: {errors}"
                
                # Verificar que todas as consultas retornaram dados
                successful_queries = [r for r in all_results if r[0] != 'erro']
                assert len(successful_queries) == 40  # 10 threads * 4 consultas cada
                
                print(f"Consultas simultâneas executadas com sucesso: {len(successful_queries)}")


class TestMemoryUsage:
    """Testes de uso de memória"""
    
    @pytest.mark.slow
    def test_memory_usage_large_dataset(self, app):
        """Testa uso de memória com grandes volumes de dados"""
        
        try:
            import psutil
            import os
        except ImportError:
            pytest.skip("psutil não disponível")
        
        def get_memory_usage():
            """Retorna uso de memória atual em MB"""
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        
        with app.app_context():
            memory_start = get_memory_usage()
            
            # Criar muitos dados
            produtos = []
            for i in range(500):
                produto = ProdutoService.criar_produto(
                    f'Produto Memory {i}',
                    valor_compra=10.0,
                    valor_venda=15.0,
                    quantidade=100
                )
                produtos.append(produto)
                
                # Adicionar movimentos
                for j in range(20):
                    MovimentoService.registrar_entrada(produto.id, 5, 10.0)
                    MovimentoService.registrar_saida(produto.id, 2, 15.0)
            
            memory_after_data = get_memory_usage()
            
            # Executar consultas que carregam todos os dados
            from app.services.relatorio_service import RelatorioService
            
            for _ in range(10):
                RelatorioService.relatorio_estoque()
                RelatorioService.relatorio_diario()
                RelatorioService.dashboard()
            
            memory_after_queries = get_memory_usage()
            
            memory_increase = memory_after_queries - memory_start
            
            # O aumento de memória não deve ser excessivo (< 200MB)
            assert memory_increase < 200
            
            print(f"Memória inicial: {memory_start:.2f} MB")
            print(f"Memória após dados: {memory_after_data:.2f} MB")
            print(f"Memória após consultas: {memory_after_queries:.2f} MB")
            print(f"Aumento total: {memory_increase:.2f} MB")
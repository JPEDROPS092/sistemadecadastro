#!/usr/bin/env python3
"""
Script para executar todos os testes do sistema
"""

import os
import sys
import subprocess


def run_tests():
    """Executa os testes do sistema"""
    
    # Definir variáveis de ambiente para testes
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    os.environ['PYTHONPATH'] = '.'
    
    print("🧪 Iniciando execução dos testes...")
    print("=" * 60)
    
    # Comandos de teste
    test_commands = [
        {
            'name': 'Testes Unitários - Autenticação',
            'cmd': ['python', '-m', 'pytest', 'tests/test_auth.py', '-v', '--tb=short'],
            'env': {'PYTHONPATH': '.', 'FLASK_ENV': 'testing', 'TESTING': 'True'}
        },
        {
            'name': 'Testes Unitários - Produtos',
            'cmd': ['python', '-m', 'pytest', 'tests/test_produtos.py', '-v', '--tb=short'],
            'env': {'PYTHONPATH': '.', 'FLASK_ENV': 'testing', 'TESTING': 'True'}
        },
        {
            'name': 'Testes Unitários - Movimentos',
            'cmd': ['python', '-m', 'pytest', 'tests/test_movimentos.py', '-v', '--tb=short'],
            'env': {'PYTHONPATH': '.', 'FLASK_ENV': 'testing', 'TESTING': 'True'}
        },
        {
            'name': 'Testes Unitários - Caixa',
            'cmd': ['python', '-m', 'pytest', 'tests/test_caixa.py', '-v', '--tb=short'],
            'env': {'PYTHONPATH': '.', 'FLASK_ENV': 'testing', 'TESTING': 'True'}
        },
        {
            'name': 'Testes Unitários - Relatórios',
            'cmd': ['python', '-m', 'pytest', 'tests/test_relatorios.py', '-v', '--tb=short'],
            'env': {'PYTHONPATH': '.', 'FLASK_ENV': 'testing', 'TESTING': 'True'}
        },
        {
            'name': 'Testes de Integração - Fluxo Completo',
            'cmd': ['python', '-m', 'pytest', 'tests/test_integration.py', '-v', '--tb=short'],
            'env': {'PYTHONPATH': '.', 'FLASK_ENV': 'testing', 'TESTING': 'True'}
        }
    ]
    
    # Executar cada conjunto de testes
    total_success = True
    results = []
    
    for test_group in test_commands:
        print(f"\n🔍 {test_group['name']}")
        print("-" * 50)
        
        try:
            # Configurar ambiente para o subprocess
            env = os.environ.copy()
            if 'env' in test_group:
                env.update(test_group['env'])
            
            result = subprocess.run(
                test_group['cmd'],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos timeout
                env=env
            )
            
            if result.returncode == 0:
                print(f"✅ {test_group['name']}: PASSOU")
                results.append((test_group['name'], 'PASSOU', result.stdout))
            else:
                print(f"❌ {test_group['name']}: FALHOU")
                results.append((test_group['name'], 'FALHOU', result.stdout + result.stderr))
                total_success = False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_group['name']}: TIMEOUT")
            results.append((test_group['name'], 'TIMEOUT', 'Teste excedeu tempo limite'))
            total_success = False
        except Exception as e:
            print(f"💥 {test_group['name']}: ERRO - {str(e)}")
            results.append((test_group['name'], 'ERRO', str(e)))
            total_success = False
    
    # Executar todos os testes com cobertura
    print(f"\n📊 Executando todos os testes com cobertura...")
    print("-" * 50)
    
    try:
        coverage_cmd = [
            'python', '-m', 'pytest', 
            'tests/', 
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-fail-under=40',
            '-v'
        ]
        
        # Configurar ambiente
        env = os.environ.copy()
        env.update({'PYTHONPATH': '.', 'FLASK_ENV': 'testing', 'TESTING': 'True'})
        
        coverage_result = subprocess.run(
            coverage_cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutos para todos os testes
            env=env
        )
        
        print(coverage_result.stdout)
        if coverage_result.stderr:
            print("Avisos:", coverage_result.stderr)
            
    except Exception as e:
        print(f"Erro na análise de cobertura: {e}")
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    
    for name, status, output in results:
        status_emoji = "✅" if status == "PASSOU" else "❌"
        print(f"{status_emoji} {name}: {status}")
    
    if total_success:
        print("\n🎉 TODOS OS TESTES PASSARAM! 🎉")
        print("✨ O sistema está funcionando corretamente")
        return 0
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima e corrija antes de continuar")
        
        # Mostrar detalhes dos testes que falharam
        print("\n📝 DETALHES DOS TESTES QUE FALHARAM:")
        print("-" * 50)
        for name, status, output in results:
            if status != "PASSOU":
                print(f"\n🔍 {name} ({status}):")
                print(output[:1000])  # Primeiros 1000 caracteres do erro
                if len(output) > 1000:
                    print("... (saída truncada)")
        
        return 1


def run_specific_tests():
    """Permite executar testes específicos"""
    
    if len(sys.argv) < 2:
        print("Uso: python run_tests.py [all|auth|produtos|movimentos|caixa|relatorios|integration]")
        return 1
    
    test_type = sys.argv[1].lower()
    
    test_files = {
        'all': 'tests/',
        'auth': 'tests/test_auth.py',
        'produtos': 'tests/test_produtos.py', 
        'movimentos': 'tests/test_movimentos.py',
        'caixa': 'tests/test_caixa.py',
        'relatorios': 'tests/test_relatorios.py',
        'integration': 'tests/test_integration.py'
    }
    
    if test_type not in test_files:
        print(f"Tipo de teste inválido: {test_type}")
        print("Opções disponíveis:", list(test_files.keys()))
        return 1
    
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    os.environ['PYTHONPATH'] = '.'
    
    cmd = ['python', '-m', 'pytest', test_files[test_type], '-v', '--tb=short']
    
    if test_type == 'all':
        cmd.extend(['--cov=app', '--cov-report=term-missing'])
    
    print(f"🧪 Executando testes: {test_type}")
    print("Comando:", ' '.join(cmd))
    print("-" * 50)
    
    try:
        # Configurar ambiente
        env = os.environ.copy()
        env.update({'PYTHONPATH': '.', 'FLASK_ENV': 'testing', 'TESTING': 'True'})
        
        result = subprocess.run(cmd, timeout=600, env=env)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("⏰ Testes excederam tempo limite")
        return 1
    except Exception as e:
        print(f"💥 Erro ao executar testes: {e}")
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        exit_code = run_specific_tests()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)
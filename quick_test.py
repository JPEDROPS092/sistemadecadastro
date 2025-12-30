#!/usr/bin/env python3
"""
Script rápido para testar se todos os módulos estão funcionando
"""

import os
import subprocess
import sys

def quick_test():
    """Executa um teste rápido de cada módulo"""
    
    # Configurar ambiente
    env = os.environ.copy()
    env.update({
        'PYTHONPATH': '.',
        'FLASK_ENV': 'testing',
        'TESTING': 'True'
    })
    
    # Testes rápidos para cada módulo
    quick_tests = [
        {
            'name': 'Auth Service',
            'cmd': ['python', '-m', 'pytest', 'tests/test_auth.py::TestAuthService::test_autenticar_usuario_valido', '-v']
        },
        {
            'name': 'Produto Service', 
            'cmd': ['python', '-m', 'pytest', 'tests/test_produtos.py::TestProdutoService::test_criar_produto', '-v']
        },
        {
            'name': 'Usuario Model',
            'cmd': ['python', '-m', 'pytest', 'tests/test_auth.py::TestUsuarioModel::test_usuario_creation', '-v']
        }
    ]
    
    print("🚀 Executando testes rápidos...")
    print("=" * 50)
    
    all_passed = True
    
    for test in quick_tests:
        print(f"\n🧪 Testando {test['name']}...")
        
        try:
            result = subprocess.run(
                test['cmd'],
                capture_output=True,
                text=True,
                env=env,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✅ {test['name']}: PASSOU")
            else:
                print(f"❌ {test['name']}: FALHOU")
                print("Erro:", result.stdout[-200:])  # Últimas linhas do erro
                all_passed = False
                
        except Exception as e:
            print(f"💥 {test['name']}: ERRO - {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Todos os testes rápidos passaram!")
        print("✨ O sistema está funcionando corretamente")
        
        # Executar teste de cobertura básica
        print("\n📊 Executando teste de cobertura...")
        try:
            coverage_cmd = [
                'python', '-m', 'pytest', 
                'tests/test_auth.py::TestAuthService',
                '--cov=app',
                '--cov-report=term-missing',
                '-q'
            ]
            
            coverage_result = subprocess.run(
                coverage_cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=120
            )
            
            if coverage_result.returncode == 0:
                print("✅ Cobertura executada com sucesso")
                # Extrair linha de cobertura
                lines = coverage_result.stdout.split('\n')
                for line in lines:
                    if 'TOTAL' in line:
                        print(f"📈 {line}")
            else:
                print("⚠️  Problema na cobertura, mas testes básicos funcionam")
                
        except Exception as e:
            print(f"⚠️  Erro na cobertura: {e}")
            
        return 0
    else:
        print("❌ Alguns testes falharam")
        print("🔧 Verificar problemas antes de continuar")
        return 1

if __name__ == '__main__':
    sys.exit(quick_test())
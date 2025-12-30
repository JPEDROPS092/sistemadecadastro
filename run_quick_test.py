#!/usr/bin/env python3
"""
Script para executar testes rápidos e ver o progresso das correções
"""
import os
import subprocess
import sys

def run_test_module(module_name):
    """Executa um módulo específico de testes"""
    print(f"\n{'='*50}")
    print(f"🧪 TESTANDO {module_name.upper()}")
    print(f"{'='*50}")
    
    env = os.environ.copy()
    env['PYTHONPATH'] = '/home/pedro/Projetos/sistemadecadastro'
    
    cmd = [
        sys.executable, '-m', 'pytest', 
        f'tests/{module_name}', 
        '-v', '--tb=short'
    ]
    
    try:
        result = subprocess.run(cmd, cwd='/home/pedro/Projetos/sistemadecadastro', 
                              env=env, capture_output=True, text=True)
        
        # Extrair informações do resultado
        output = result.stdout
        failed_count = output.count('FAILED')
        passed_count = output.count('PASSED')
        error_count = output.count('ERROR')
        
        print(f"✅ PASSOU: {passed_count}")
        print(f"❌ FALHOU: {failed_count}")
        print(f"🚨 ERRO: {error_count}")
        
        if failed_count > 0 or error_count > 0:
            # Mostrar apenas as falhas principais
            lines = output.split('\n')
            for line in lines:
                if 'FAILED' in line or 'ERROR' in line:
                    print(f"  {line}")
        
        return {
            'module': module_name,
            'passed': passed_count,
            'failed': failed_count,
            'errors': error_count,
            'total': passed_count + failed_count + error_count
        }
        
    except Exception as e:
        print(f"Erro ao executar testes de {module_name}: {e}")
        return None


def main():
    modules_to_test = [
        'test_auth.py',
        'test_produtos.py', 
        'test_caixa.py',
        'test_movimentos.py',
        'test_relatorios.py'
    ]
    
    results = []
    
    for module in modules_to_test:
        result = run_test_module(module)
        if result:
            results.append(result)
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO GERAL DOS TESTES")
    print(f"{'='*60}")
    
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_tests = 0
    
    for result in results:
        module = result['module'].replace('.py', '').upper()
        passed = result['passed']
        failed = result['failed']
        errors = result['errors']
        total = result['total']
        
        status = "✅" if failed == 0 and errors == 0 else "❌"
        print(f"{status} {module:<15} | {passed:>3} passou | {failed:>3} falhou | {errors:>3} erro | {total:>3} total")
        
        total_passed += passed
        total_failed += failed
        total_errors += errors
        total_tests += total
    
    print(f"{'='*60}")
    print(f"{'TOTAL':<17} | {total_passed:>3} passou | {total_failed:>3} falhou | {total_errors:>3} erro | {total_tests:>3} total")
    
    # Calcular percentual de sucesso
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"\n🎯 Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🏆 Excelente! Quase todos os testes passando!")
        elif success_rate >= 75:
            print("👍 Bom progresso! Maioria dos testes passando.")
        elif success_rate >= 50:
            print("⚠️  Progresso moderado. Ainda há trabalho a fazer.")
        else:
            print("🚨 Muitos testes falhando. Precisa de mais correções.")
    
    return total_failed + total_errors == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
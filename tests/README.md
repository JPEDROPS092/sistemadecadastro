# 🧪 Testes do Sistema de Cadastro

Este diretório contém uma suíte completa de testes para o sistema de cadastro, cobrindo todas as funcionalidades e fluxos da aplicação.

## 📁 Estrutura dos Testes

```
tests/
├── conftest.py              # Configurações e fixtures dos testes
├── test_auth.py             # Testes de autenticação e usuários
├── test_produtos.py         # Testes do módulo de produtos
├── test_movimentos.py       # Testes de movimentos de estoque
├── test_caixa.py           # Testes do módulo de caixa
├── test_relatorios.py      # Testes de relatórios e dashboard
├── test_integration.py     # Testes de integração e fluxos completos
├── test_performance.py     # Testes de performance e stress
└── README.md              # Este arquivo
```

## 🎯 Cobertura dos Testes

### 🔐 Autenticação (`test_auth.py`)
- ✅ Login e logout de usuários
- ✅ Controle de permissões (admin, gerente, operador)
- ✅ Criação e gerenciamento de usuários
- ✅ Alteração de senhas
- ✅ Validações de segurança

### 📦 Produtos (`test_produtos.py`)
- ✅ CRUD completo de produtos
- ✅ Controle de estoque e alertas de estoque baixo
- ✅ Validações de dados de entrada
- ✅ Cálculos de margem de lucro
- ✅ Listagens e filtros

### 📊 Movimentos de Estoque (`test_movimentos.py`)
- ✅ Registro de entradas e saídas
- ✅ Atualização automática de estoque
- ✅ Controle de estoque insuficiente
- ✅ Filtros por período e produto
- ✅ Cálculos de valores totais

### 💰 Caixa (`test_caixa.py`)
- ✅ Abertura e fechamento de caixa
- ✅ Registro de movimentos financeiros
- ✅ Controle de saldo e validações
- ✅ Integração com vendas
- ✅ Histórico de caixas

### 📈 Relatórios (`test_relatorios.py`)
- ✅ Dashboard com indicadores
- ✅ Relatórios de estoque
- ✅ Relatórios de movimentos
- ✅ Relatórios de caixa e fluxo
- ✅ Performance com grandes volumes

### 🔄 Integração (`test_integration.py`)
- ✅ Fluxo completo de venda
- ✅ Gestão integrada de estoque
- ✅ Operações diárias de caixa
- ✅ Geração de relatórios completos
- ✅ Controle de permissões
- ✅ Tratamento de erros

### ⚡ Performance (`test_performance.py`)
- ✅ Testes de carga com muitos dados
- ✅ Concorrência e thread safety
- ✅ Uso de memória
- ✅ Tempo de resposta de relatórios

## 🚀 Como Executar os Testes

### Pré-requisitos
```bash
# Instalar dependências de teste
pip install pytest pytest-flask pytest-cov psutil
```

### Executar Todos os Testes
```bash
# Executar suíte completa
python run_tests.py

# Ou usando pytest diretamente
pytest tests/ -v --cov=app
```

### Executar Testes Específicos
```bash
# Testes de autenticação
python run_tests.py auth

# Testes de produtos
python run_tests.py produtos

# Testes de movimentos
python run_tests.py movimentos

# Testes de caixa
python run_tests.py caixa

# Testes de relatórios
python run_tests.py relatorios

# Testes de integração
python run_tests.py integration
```

### Executar Testes com Filtros
```bash
# Apenas testes rápidos (excluir performance)
pytest tests/ -v -m "not slow"

# Apenas testes de integração
pytest tests/test_integration.py -v

# Testes com cobertura detalhada
pytest tests/ --cov=app --cov-report=html
```

## 📊 Relatórios de Cobertura

Os testes geram relatórios de cobertura automáticos:

```bash
# Relatório no terminal
pytest tests/ --cov=app --cov-report=term-missing

# Relatório HTML (salvo em htmlcov/)
pytest tests/ --cov=app --cov-report=html

# Ambos os formatos
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html
```

## 🎯 Metas de Cobertura

- **Meta mínima**: 80% de cobertura
- **Meta ideal**: 90% de cobertura
- **Cobertura atual**: Verificar com `pytest --cov`

### Áreas Cobertas:
- ✅ Rotas (blueprints): 95%+
- ✅ Serviços (business logic): 90%+
- ✅ Modelos (models): 85%+
- ✅ Utilitários: 80%+

## 🧩 Fixtures Disponíveis

### Fixtures Básicas
- `app`: Instância da aplicação Flask para testes
- `client`: Cliente de teste HTTP
- `admin_user`: Usuário administrador
- `operador_user`: Usuário operador

### Fixtures de Autenticação
- `authenticated_admin_client`: Cliente autenticado como admin
- `authenticated_operador_client`: Cliente autenticado como operador
- `auth`: Helper para operações de login/logout

### Fixtures de Dados
- `produto_teste`: Produto pré-criado para testes
- `caixa_aberto`: Caixa aberto para testes
- `movimento_teste`: Movimento de estoque para testes

## 🔧 Configuração dos Testes

### Arquivo `pytest.ini`
```ini
[tool:pytest]
testpaths = tests
addopts = -v --tb=short --cov=app --cov-fail-under=80
markers =
    slow: testes de performance (demorados)
    integration: testes de integração
    unit: testes unitários
```

### Variáveis de Ambiente
```bash
export FLASK_ENV=testing
export TESTING=True
```

## 🐛 Debugging de Testes

### Executar um Teste Específico
```bash
# Teste específico por nome
pytest tests/test_auth.py::TestAuthBlueprint::test_login_success -v

# Com debugging
pytest tests/test_auth.py::TestAuthBlueprint::test_login_success -v -s --pdb
```

### Ver Output Detalhado
```bash
# Mostrar prints e logs
pytest tests/ -v -s

# Traceback completo em falhas
pytest tests/ -v --tb=long
```

## 📝 Escrevendo Novos Testes

### Estrutura Básica
```python
import pytest
from app.models import MinhaModel

class TestMinhaFuncionalidade:
    """Testes para minha funcionalidade"""
    
    def test_minha_funcao(self, app, authenticated_admin_client):
        """Testa minha função específica"""
        
        # Arrange - preparar dados
        with app.app_context():
            # ... configuração
        
        # Act - executar ação
        response = authenticated_admin_client.post('/minha-rota', data={
            'campo': 'valor'
        })
        
        # Assert - verificar resultado
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower()
```

### Boas Práticas
1. **Nome descritivo**: `test_deve_criar_produto_com_dados_validos`
2. **Arrange-Act-Assert**: Estrutura clara dos testes
3. **Isolamento**: Cada teste deve ser independente
4. **Fixture apropriada**: Use fixtures para dados de teste
5. **Verificações múltiplas**: Teste vários aspectos do resultado

## 🏃‍♂️ Integração Contínua

### Executar na CI/CD
```bash
# Script para CI/CD
#!/bin/bash
set -e

echo "🧪 Executando testes..."
python -m pytest tests/ --cov=app --cov-report=xml --cov-fail-under=80

echo "✅ Todos os testes passaram!"
```

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-flask pytest-cov
      - name: Run tests
        run: python run_tests.py
```

## 📈 Métricas de Qualidade

### O que Medimos:
- **Cobertura de código**: Linhas executadas pelos testes
- **Tempo de execução**: Performance dos testes
- **Taxa de sucesso**: Percentual de testes que passam
- **Cobertura de fluxos**: Cenários de negócio testados

### Relatórios Gerados:
- `htmlcov/index.html`: Relatório visual de cobertura
- Terminal: Resumo de execução e cobertura
- JUnit XML: Para integração com ferramentas CI/CD

## 🎉 Benefícios dos Testes

### ✅ Qualidade Assegurada
- Detecta bugs antes da produção
- Valida todas as funcionalidades
- Garante que mudanças não quebram funcionalidades existentes

### 🚀 Confiança para Deploy
- Suite completa de testes passa = código pronto para produção
- Cobertura alta = menor chance de bugs
- Testes de integração = fluxos funcionando corretamente

### 🔧 Manutenibilidade
- Testes servem como documentação viva
- Refatorações seguras com testes como rede de segurança
- Detecta regressões rapidamente

### 🏗️ Desenvolvimento Robusto
- TDD: Escrever testes primeiro orienta o design
- Feedback rápido durante desenvolvimento
- Facilita colaboração em equipe

---

**📞 Suporte**: Para dúvidas sobre os testes, consulte a documentação do código ou abra uma issue no repositório.
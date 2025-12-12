# Sistema de Gestão de Estoque e Caixa

Sistema completo de gestão com controle de estoque, caixa e relatórios, desenvolvido com Flask.

## Funcionalidades

### Autenticação e Controle de Acesso
- Sistema de login com 3 níveis de acesso (Admin, Gerente, Operador)
- Proteção de rotas por autenticação
- Gerenciamento de usuários (apenas para Admin)
- Alteração de senha

### Gestão de Produtos
- Cadastro, edição e exclusão de produtos
- Controle de estoque mínimo
- Alertas de estoque baixo
- Cálculo automático de margem de lucro

### Controle de Movimentos
- Registro de entradas (compras)
- Registro de saídas (vendas)
- Histórico completo de movimentações
- Filtros por produto, tipo e período

### Controle de Caixa
- Abertura e fechamento de caixa
- Registro de movimentos financeiros
- Categorização de transações
- Histórico de caixas
- Integração automática com vendas

### Relatórios
- Dashboard com visão geral do negócio
- Relatório de estoque
- Relatório de movimentos (diário, semanal, mensal)
- Relatório de fluxo diário completo
- Relatório de caixa
- Gráficos interativos com Chart.js

## Tecnologias

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Frontend:** HTML5, CSS3 (Responsivo), JavaScript
- **Banco de Dados:** SQLite
- **Gráficos:** Chart.js

## Estrutura do Projeto

```
sistemadecadastro/
├── app/
│   ├── blueprints/         # Rotas organizadas por módulo
│   │   ├── main.py
│   │   ├── produtos.py
│   │   ├── movimentos.py
│   │   ├── caixa.py
│   │   ├── relatorios.py
│   │   └── auth.py
│   ├── models/             # Modelos do banco de dados
│   │   ├── produto.py
│   │   ├── movimento.py
│   │   ├── caixa.py
│   │   └── usuario.py
│   ├── services/           # Lógica de negócio
│   │   ├── produto_service.py
│   │   ├── movimento_service.py
│   │   ├── caixa_service.py
│   │   ├── relatorio_service.py
│   │   └── auth_service.py
│   ├── templates/          # Templates HTML
│   ├── static/             # CSS, JS e imagens
│   └── utils/              # Utilitários e decoradores
├── run.py                  # Arquivo principal
├── config.py               # Configurações
├── migrate_db.py          # Script de migração
└── requirements.txt        # Dependências
```

## Instalação

1. Clone o repositório
```bash

cd sistemadecadastro
```

2. Crie e ative o ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Execute as migrações do banco de dados (se necessário)
```bash
python migrate_db.py
```

5. Inicie o servidor
```bash
python run.py
```

6. Acesse o sistema em `http://localhost:5000`

## Usuários Padrão

O sistema cria automaticamente 3 usuários de teste:

| Usuário   | Senha       | Tipo          | Permissões                          |
|-----------|-------------|---------------|-------------------------------------|
| admin     | admin123    | Administrador | Acesso total + gerenciamento users  |
| gerente   | gerente123  | Gerente       | Acesso total ao sistema             |
| operador  | operador123 | Operador      | Acesso ao sistema                   |

**IMPORTANTE:** Altere as senhas padrão em produção!

## Uso

### Dashboard
- Visualize estatísticas gerais do negócio
- Acompanhe vendas e lucro do dia
- Monitore produtos com estoque baixo
- Veja os produtos mais vendidos

### Produtos
- Cadastre novos produtos com valores de compra e venda
- Defina estoque mínimo para alertas
- Edite ou desative produtos
- Visualize margem de lucro

### Movimentos
- Registre entradas (compras) no estoque
- Registre saídas (vendas) com integração ao caixa
- Filtre movimentos por produto, tipo e período

### Caixa
- Abra o caixa informando saldo inicial
- Registre movimentos financeiros (vendas, despesas, receitas)
- Vendas são registradas automaticamente
- Feche o caixa ao final do dia
- Consulte histórico de caixas

### Relatórios
- **Estoque:** Valor investido, valor potencial, lucro potencial
- **Movimentos:** Análise de vendas e compras por período
- **Fluxo Diário:** Visão completa do dia (estoque + caixa)
- **Caixa:** Análise detalhada do caixa atual

## Segurança

- Senhas criptografadas com Werkzeug
- Proteção de rotas com Flask-Login
- Controle de acesso por nível de usuário
- Validações de entrada de dados

## Licença

Este projeto está sob a licença MIT.

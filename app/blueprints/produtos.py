from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services import ProdutoService, MovimentoService
from app.models import Produto

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

## --- LISTAGEM E BUSCA ---

@produtos_bp.route('/')
@login_required
def listar():
    produtos = ProdutoService.listar_produtos()
    return render_template('produtos/lista.html', produtos=produtos)

@produtos_bp.route('/estoque-baixo')
@login_required
def estoque_baixo():
    produtos = ProdutoService.produtos_estoque_baixo()
    return render_template('produtos/lista.html', produtos=produtos, filtro="baixo")

@produtos_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if query:
        # Busca direta no model para agilidade, mas o ideal seria via Service
        produtos = Produto.query.filter(Produto.nome.ilike(f'%{query}%')).limit(10).all()
    else:
        produtos = ProdutoService.listar_produtos()[:10]
    return render_template('produtos/_table_rows.html', produtos=produtos)


## --- CRIAÇÃO E EDIÇÃO ---

@produtos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        try:
            # Capturamos os dados garantindo tipos numéricos básicos
            ProdutoService.criar_produto(
                nome=request.form.get('nome'), 
                valor_compra=float(request.form.get('valor_compra', 0)), 
                valor_venda=float(request.form.get('valor_venda', 0)), 
                quantidade=int(request.form.get('quantidade', 0)), 
                estoque_minimo=int(request.form.get('estoque_minimo', 5))
            )
            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('produtos.listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            
    return render_template('produtos/form.html', produto=None)

@produtos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    produto = ProdutoService.obter_produto(id)
    if not produto:
        flash('Produto não encontrado!', 'danger')
        return redirect(url_for('produtos.listar'))

    if request.method == 'POST':
        try:
            ProdutoService.atualizar_produto(
                id, 
                nome=request.form.get('nome'),
                valor_compra=float(request.form.get('valor_compra', 0)),
                valor_venda=float(request.form.get('valor_venda', 0)),
                estoque_minimo=int(request.form.get('estoque_minimo', 5))
            )
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('produtos.listar'))
        except Exception as e:
            flash(f'Erro ao atualizar: {str(e)}', 'danger')

    return render_template('produtos/form.html', produto=produto)


## --- OPERAÇÕES DE ESTOQUE E EXCLUSÃO ---

@produtos_bp.route('/update_qtd/<int:id>', methods=['POST'])
@login_required
def update_qtd(id):
    """ Rota otimizada para requisições HTMX de reposição rápida """
    try:
        val = request.form.get('qtd_adicional')
        if not val or int(val) <= 0:
            return 'Quantidade inválida', 400
            
        quantidade = int(val)

        # 1. Atualiza estoque no banco
        if ProdutoService.atualizar_estoque(id, quantidade):
            # 2. Registra o movimento para histórico/auditoria
            MovimentoService.registrar_entrada(
                produto_id=id, 
                quantidade=quantidade, 
                motivo="Reposição via painel de produto"
            )
            return '', 204 # Sucesso silencioso para HTMX
            
        return 'Erro ao atualizar banco', 500
        
    except ValueError:
        return 'Insira um número inteiro', 400
    except Exception as e:
        return f'Erro: {str(e)}', 500

@produtos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    if ProdutoService.excluir_produto(id):
        flash('Produto removido com sucesso!', 'success')
    else:
        flash('Erro ao remover produto.', 'danger')
    return redirect(url_for('produtos.listar'))
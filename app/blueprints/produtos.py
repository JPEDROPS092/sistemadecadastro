from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.services import ProdutoService, MovimentoService

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

@produtos_bp.route('/')
@login_required
def listar():
    produtos = ProdutoService.listar_produtos()
    return render_template('produtos/lista.html', produtos=produtos)

@produtos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            valor_compra = float(request.form.get('valor_compra'))
            valor_venda = float(request.form.get('valor_venda'))
            qtd = int(request.form.get('quantidade', 0))
            estoque_minimo = int(request.form.get('estoque_minimo', 5))

            produto = ProdutoService.criar_produto(nome, valor_compra, valor_venda, qtd, estoque_minimo)

            if qtd > 0:
                MovimentoService.registrar_entrada(produto.id, qtd, valor_compra, "Estoque inicial")

            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('produtos.listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar produto: {str(e)}', 'error')

    return render_template('produtos/form.html', produto=None)

@produtos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    produto = ProdutoService.obter_produto(id)
    if not produto:
        flash('Produto não encontrado', 'error')
        return redirect(url_for('produtos.listar'))

    if request.method == 'POST':
        try:
            dados = {
                'nome': request.form.get('nome'),
                'valor_compra': float(request.form.get('valor_compra')),
                'valor_venda': float(request.form.get('valor_venda')),
                'estoque_minimo': int(request.form.get('estoque_minimo'))
            }
            ProdutoService.atualizar_produto(id, **dados)
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('produtos.listar'))
        except Exception as e:
            flash(f'Erro ao atualizar produto: {str(e)}', 'error')

    return render_template('produtos/form.html', produto=produto)

@produtos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    try:
        ProdutoService.excluir_produto(id)
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir produto: {str(e)}', 'error')

    return redirect(url_for('produtos.listar'))

@produtos_bp.route('/estoque-baixo')
@login_required
def estoque_baixo():
    produtos = ProdutoService.produtos_estoque_baixo()
    return render_template('produtos/estoque_baixo.html', produtos=produtos)

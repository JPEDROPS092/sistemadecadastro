from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Produto, Movimento
from app.services import CaixaService, ProdutoService, MovimentoService

caixa_bp = Blueprint('caixa', __name__, url_prefix='/caixa')

@caixa_bp.route('/')
@login_required
def index():
    caixa = CaixaService.obter_caixa_aberto()
    movimentos = []
    if caixa:
        movimentos = CaixaService.listar_movimentos_caixa(caixa.id)
    
    produtos = ProdutoService.listar_produtos()
    return render_template(
        'caixa/index.html',
        caixa=caixa,
        movimentos=movimentos,
        produtos=produtos
    )

@caixa_bp.route('/abrir', methods=['POST'])
@login_required
def abrir():
    try:
        # Conversão segura para float para evitar erros de string vazia
        valor_raw = request.form.get('saldo_inicial', '0').replace(',', '.')
        saldo_inicial = float(valor_raw) if valor_raw else 0.0
        
        CaixaService.abrir_caixa(saldo_inicial=saldo_inicial)
        db.session.commit()
        
        flash(f'Caixa aberto com sucesso! Saldo inicial: R$ {saldo_inicial:.2f}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao abrir caixa: {str(e)}', 'danger')
    
    return redirect(url_for('caixa.index'))

@caixa_bp.route('/adicionar_item', methods=['POST'])
@login_required
def adicionar_item():
    produto_id = request.form.get('produto_id')
    try:
        quantidade = int(request.form.get('quantidade', 1))
        produto = Produto.query.get(produto_id)
        
        if not produto:
            return "Produto não encontrado", 404
            
        # FORÇAR ATUALIZAÇÃO DO ESTOQUE (Evita o erro de contagem errada)
        db.session.refresh(produto)

        if produto.qtd < quantidade:
            return f"Estoque insuficiente (Disponível: {produto.qtd})", 400

        total_item = produto.valor_venda * quantidade
        return render_template(
            'caixa/_item_venda.html',
            produto=produto,
            quantidade=quantidade,
            total_item=total_item
        )
    except Exception as e:
        return f"Erro: {str(e)}", 500

@caixa_bp.route('/finalizar', methods=['POST'])
@login_required
def finalizar():
    try:
        produto_ids = request.form.getlist('produto_ids[]')
        quantidades = request.form.getlist('quantidades[]')
        forma_pagamento = request.form.get('forma_pagamento')

        if not produto_ids:
            flash('Carrinho vazio!', 'warning')
            return redirect(url_for('caixa.index'))

        caixa = CaixaService.obter_caixa_aberto()
        if not caixa:
            flash('Abra o caixa antes de vender!', 'danger')
            return redirect(url_for('caixa.index'))

        total_venda = 0
        for p_id, qtd_venda in zip(produto_ids, quantidades):
            produto = Produto.query.get(p_id)
            if not produto: continue
            
            # ATUALIZAÇÃO CRÍTICA: Lê o estoque real do PostgreSQL agora
            db.session.refresh(produto)
            qtd_venda = int(qtd_venda)

            if produto.qtd < qtd_venda:
                db.session.rollback()
                flash(f'Estoque insuficiente para {produto.nome} (Disponível: {produto.qtd})', 'danger')
                return redirect(url_for('caixa.index'))

            # Baixa no estoque real
            produto.qtd -= qtd_venda
            total_venda += (produto.valor_venda * qtd_venda)
            
            # Registra no histórico de movimentação
            MovimentoService.registrar_saida(produto.id, qtd_venda, f"Venda PDV - Caixa #{caixa.id}")

        # Registra no financeiro do caixa
        CaixaService.registrar_venda(caixa.id, total_venda, forma_pagamento)
        
        db.session.commit()
        flash(f'Venda de R$ {total_venda:.2f} finalizada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro técnico ao finalizar: {str(e)}', 'danger')
    
    return redirect(url_for('caixa.index'))

@caixa_bp.route('/fechar', methods=['POST'])
@login_required
def fechar():
    try:
        caixa = CaixaService.obter_caixa_aberto()
        if not caixa:
            flash('Não há caixa aberto.', 'warning')
            return redirect(url_for('caixa.index'))

        observacao = request.form.get('observacao', '')
        CaixaService.fechar_caixa(caixa.id, observacao)
        db.session.commit()
        
        flash('Caixa encerrado com sucesso!', 'success')
        return redirect(url_for('caixa.historico'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao fechar: {str(e)}', 'danger')
        return redirect(url_for('caixa.index'))

@caixa_bp.route('/historico')
@login_required
def historico():
    # Agora puxa os dados do Movimento conforme corrigido anteriormente
    historico_caixa = CaixaService.listar_historico_fechamentos() 
    return render_template('caixa/historico.html', historico=historico_caixa)
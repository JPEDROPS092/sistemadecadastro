from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from app.models import db  # Importante para o db.session.commit()
from app.services import MovimentoService, ProdutoService, CaixaService

# 1. DEFINIÇÃO DO BLUEPRINT
movimentos_bp = Blueprint('movimentos', __name__, url_prefix='/movimentos')

@movimentos_bp.route('/')
@login_required
def listar():
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    produto_id = request.args.get('produto_id')
    tipo = request.args.get('tipo')

    data_inicio = datetime.fromisoformat(data_inicio_str) if data_inicio_str else None
    data_fim = datetime.fromisoformat(data_fim_str) if data_fim_str else None

    movimentos = MovimentoService.listar_movimentos(
        produto_id=produto_id,
        tipo=tipo,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

    produtos = ProdutoService.listar_produtos()
    return render_template('movimentos/lista.html', movimentos=movimentos, produtos=produtos)

@movimentos_bp.route('/entrada', methods=['GET', 'POST'])
@login_required
def entrada():
    if request.method == 'POST':
        try:
            produto_id = int(request.form.get('produto_id'))
            quantidade = int(request.form.get('quantidade'))
            observacao = request.form.get('observacao', 'Entrada manual')
            
            # Tratamento do Valor Unitário
            valor_raw = request.form.get('valor_unitario')
            if valor_raw and valor_raw.strip():
                valor_unitario = float(valor_raw.replace(',', '.'))
            else:
                produto = ProdutoService.obter_produto(produto_id)
                valor_unitario = produto.valor_custo if produto.valor_custo else 0.0

            # Chama o serviço (que agora não dá commit sozinho)
            MovimentoService.registrar_entrada(produto_id, quantidade, valor_unitario, observacao)
            
            # Único ponto de salvamento no banco de dados
            db.session.commit()
            
            flash('Entrada manual registrada com sucesso!', 'success')
            return redirect(url_for('movimentos.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar entrada: {str(e)}', 'error')

    produtos = ProdutoService.listar_produtos()
    return render_template('movimentos/entrada.html', produtos=produtos)

@movimentos_bp.route('/saida', methods=['GET', 'POST'])
@login_required
def saida():
    if request.method == 'POST':
        try:
            produto_id = int(request.form.get('produto_id'))
            quantidade = int(request.form.get('quantidade'))
            observacao = request.form.get('observacao', 'Saída manual')
            forma_pagamento = request.form.get('forma_pagamento')
            
            valor_raw = request.form.get('valor_unitario')
            if valor_raw and valor_raw.strip():
                valor_unitario = float(valor_raw.replace(',', '.'))
            else:
                produto = ProdutoService.obter_produto(produto_id)
                valor_unitario = produto.valor_venda if produto.valor_venda else 0.0

            # Registra o histórico de movimento
            movimento = MovimentoService.registrar_saida(produto_id, quantidade, valor_unitario, observacao)

            # Lógica Financeira do Caixa
            caixa = CaixaService.obter_caixa_aberto()
            if caixa:
                # O valor total do movimento gerado
                valor_total = movimento.quantidade * movimento.valor_unitario
                produto_obj = ProdutoService.obter_produto(produto_id)
                
                CaixaService.registrar_movimento(
                    caixa_id=caixa.id,
                    tipo='entrada', # Dinheiro entrando no caixa pela venda
                    categoria='venda',
                    descricao=f'Saída manual: {produto_obj.nome} (x{quantidade})',
                    valor=valor_total,
                    forma_pagamento=forma_pagamento
                )

            db.session.commit()
            flash('Saída registrada com sucesso!', 'success')
            return redirect(url_for('movimentos.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar saída: {str(e)}', 'error')

    produtos = ProdutoService.listar_produtos()
    return render_template('movimentos/saida.html', produtos=produtos)
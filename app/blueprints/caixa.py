from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import CaixaService

caixa_bp = Blueprint('caixa', __name__, url_prefix='/caixa')

@caixa_bp.route('/')
def index():
    caixa = CaixaService.obter_caixa_aberto()
    movimentos = []

    if caixa:
        movimentos = CaixaService.listar_movimentos_caixa(caixa.id)

    return render_template('caixa/index.html', caixa=caixa, movimentos=movimentos)

@caixa_bp.route('/abrir', methods=['POST'])
def abrir():
    try:
        saldo_inicial = float(request.form.get('saldo_inicial', 0))
        observacao = request.form.get('observacao')

        CaixaService.abrir_caixa(saldo_inicial, observacao)
        flash('Caixa aberto com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao abrir caixa: {str(e)}', 'error')

    return redirect(url_for('caixa.index'))

@caixa_bp.route('/fechar', methods=['POST'])
def fechar():
    try:
        caixa = CaixaService.obter_caixa_aberto()
        if not caixa:
            flash('Não há caixa aberto', 'error')
            return redirect(url_for('caixa.index'))

        observacao = request.form.get('observacao')
        CaixaService.fechar_caixa(caixa.id, observacao)
        flash('Caixa fechado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao fechar caixa: {str(e)}', 'error')

    return redirect(url_for('caixa.historico'))

@caixa_bp.route('/movimento', methods=['POST'])
def movimento():
    try:
        caixa = CaixaService.obter_caixa_aberto()
        if not caixa:
            flash('Não há caixa aberto', 'error')
            return redirect(url_for('caixa.index'))

        tipo = request.form.get('tipo')
        categoria = request.form.get('categoria')
        descricao = request.form.get('descricao')
        valor = float(request.form.get('valor'))
        forma_pagamento = request.form.get('forma_pagamento')

        CaixaService.registrar_movimento(caixa.id, tipo, categoria, descricao, valor, forma_pagamento)
        flash('Movimento registrado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao registrar movimento: {str(e)}', 'error')

    return redirect(url_for('caixa.index'))

@caixa_bp.route('/historico')
def historico():
    caixas = CaixaService.listar_caixas()
    return render_template('caixa/historico.html', caixas=caixas)

@caixa_bp.route('/<int:id>')
def detalhes(id):
    caixa = CaixaService.obter_caixa(id)
    if not caixa:
        flash('Caixa não encontrado', 'error')
        return redirect(url_for('caixa.historico'))

    movimentos = CaixaService.listar_movimentos_caixa(id)
    return render_template('caixa/detalhes.html', caixa=caixa, movimentos=movimentos)

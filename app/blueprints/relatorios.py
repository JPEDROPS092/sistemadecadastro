from flask import Blueprint, render_template, request
from flask_login import login_required
from datetime import datetime
from app.services import RelatorioService

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

@relatorios_bp.route('/')
@login_required
def index():
    return render_template('relatorios/index.html')

@relatorios_bp.route('/estoque')
@login_required
def estoque():
    relatorio = RelatorioService.relatorio_estoque()
    return render_template('relatorios/estoque.html', relatorio=relatorio)

@relatorios_bp.route('/movimentos')
@login_required
def movimentos():
    periodo = request.args.get('periodo', 'dia')

    if periodo == 'dia':
        relatorio = RelatorioService.relatorio_diario()
    elif periodo == 'semana':
        relatorio = RelatorioService.relatorio_semanal()
    elif periodo == 'mes':
        relatorio = RelatorioService.relatorio_mensal()
    else:
        data_inicio_str = request.args.get('data_inicio')
        data_fim_str = request.args.get('data_fim')

        data_inicio = datetime.fromisoformat(data_inicio_str) if data_inicio_str else None
        data_fim = datetime.fromisoformat(data_fim_str) if data_fim_str else None

        relatorio = RelatorioService.relatorio_movimentos(data_inicio, data_fim)

    return render_template('relatorios/movimentos.html', relatorio=relatorio, periodo=periodo)

@relatorios_bp.route('/fluxo-diario')
@login_required
def fluxo_diario():
    relatorio = RelatorioService.relatorio_fluxo_diario()
    return render_template('relatorios/fluxo_diario.html', relatorio=relatorio)

@relatorios_bp.route('/caixa')
@login_required
def caixa():
    caixa_id = request.args.get('caixa_id')
    if caixa_id:
        relatorio = RelatorioService.relatorio_caixa(int(caixa_id))
    else:
        relatorio = RelatorioService.relatorio_caixa()

    return render_template('relatorios/caixa.html', relatorio=relatorio)

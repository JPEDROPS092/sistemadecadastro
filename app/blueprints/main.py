from flask import Blueprint, render_template
from app.services import RelatorioService, ProdutoService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    dashboard = RelatorioService.dashboard()
    produtos = ProdutoService.listar_produtos()
    return render_template('dashboard.html', dashboard=dashboard, produtos=produtos)

import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# --- Configuração ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "estoque.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- Modelos ---
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    qtd = db.Column(db.Integer, default=0)
    valor_compra = db.Column(db.Float, nullable=False)
    valor_venda = db.Column(db.Float, nullable=False)

class Movimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' ou 'saida'
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    produto = db.relationship('Produto', backref=db.backref('movimentos', lazy=True))

# Criar tabelas
with app.app_context():
    db.create_all()

# --- Rotas principais ---
@app.route("/")
def index():
    produtos = Produto.query.all()
    return render_template("index.html", produtos=produtos)

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome = request.form.get("nome")
    qtd = int(request.form.get("quantidade"))
    valor_compra = float(request.form.get("valor_compra"))
    valor_venda = float(request.form.get("valor_venda"))

    produto = Produto(nome=nome, qtd=qtd, valor_compra=valor_compra, valor_venda=valor_venda)
    db.session.add(produto)
    db.session.commit()

    # Registrar movimento de entrada inicial
    movimento = Movimento(produto_id=produto.id, tipo='entrada', quantidade=qtd, valor_unitario=valor_compra)
    db.session.add(movimento)
    db.session.commit()

    return redirect(url_for("index"))

@app.route("/entrada/<int:id>", methods=["POST"])
def entrada(id):
    produto = Produto.query.get(id)
    qtd = int(request.form.get("quantidade"))
    produto.qtd += qtd
    db.session.commit()

    movimento = Movimento(produto_id=id, tipo='entrada', quantidade=qtd, valor_unitario=produto.valor_compra)
    db.session.add(movimento)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/saida/<int:id>", methods=["POST"])
def saida(id):
    produto = Produto.query.get(id)
    qtd = int(request.form.get("quantidade"))
    if qtd <= produto.qtd:
        produto.qtd -= qtd
        db.session.commit()

        movimento = Movimento(produto_id=id, tipo='saida', quantidade=qtd, valor_unitario=produto.valor_venda)
        db.session.add(movimento)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/limpar")
def limpar():
    db.session.query(Movimento).delete()
    db.session.query(Produto).delete()
    db.session.commit()
    return redirect(url_for("index"))

# --- Relatórios diário e semanal ---
@app.route("/relatorio")
def relatorio():
    hoje = datetime.today()
    semana_atras = hoje - timedelta(days=7)

    produtos = Produto.query.all()
    relatorio_diario = []
    relatorio_semanal = []

    for p in produtos:
        # Movimentos do dia
        movimentos_dia = Movimento.query.filter(
            Movimento.produto_id==p.id,
            Movimento.data >= hoje.replace(hour=0, minute=0, second=0, microsecond=0)
        ).all()
        total_gasto_dia = sum(m.quantidade*m.valor_unitario for m in movimentos_dia if m.tipo=='entrada')
        total_ganho_dia = sum(m.quantidade*m.valor_unitario for m in movimentos_dia if m.tipo=='saida')
        relatorio_diario.append({
            'nome': p.nome,
            'total_gasto': total_gasto_dia,
            'total_ganho': total_ganho_dia
        })

        # Movimentos da semana
        movimentos_semana = Movimento.query.filter(
            Movimento.produto_id==p.id,
            Movimento.data >= semana_atras
        ).all()
        total_gasto_sem = sum(m.quantidade*m.valor_unitario for m in movimentos_semana if m.tipo=='entrada')
        total_ganho_sem = sum(m.quantidade*m.valor_unitario for m in movimentos_semana if m.tipo=='saida')
        relatorio_semanal.append({
            'nome': p.nome,
            'total_gasto': total_gasto_sem,
            'total_ganho': total_ganho_sem
        })

    return render_template(
        "relatorio.html",
        relatorio_diario=relatorio_diario,
        relatorio_semanal=relatorio_semanal
    )

# --- Executar app ---
if __name__ == "__main__":
    app.run(debug=True)

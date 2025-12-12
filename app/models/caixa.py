from datetime import datetime
from . import db

class Caixa(db.Model):
    __tablename__ = 'caixa'

    id = db.Column(db.Integer, primary_key=True)
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    data_fechamento = db.Column(db.DateTime)
    saldo_inicial = db.Column(db.Float, default=0.0)
    saldo_final = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='aberto')  # 'aberto' ou 'fechado'
    observacao = db.Column(db.String(200))

    movimentos = db.relationship('MovimentoCaixa', backref='caixa', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Caixa {self.id} - {self.status}>'

    @property
    def total_entradas(self):
        return sum(m.valor for m in self.movimentos if m.tipo == 'entrada')

    @property
    def total_saidas(self):
        return sum(m.valor for m in self.movimentos if m.tipo == 'saida')

    @property
    def saldo_calculado(self):
        return self.saldo_inicial + self.total_entradas - self.total_saidas

    def to_dict(self):
        return {
            'id': self.id,
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'data_fechamento': self.data_fechamento.isoformat() if self.data_fechamento else None,
            'saldo_inicial': self.saldo_inicial,
            'saldo_final': self.saldo_final,
            'total_entradas': self.total_entradas,
            'total_saidas': self.total_saidas,
            'saldo_calculado': self.saldo_calculado,
            'status': self.status,
            'observacao': self.observacao
        }


class MovimentoCaixa(db.Model):
    __tablename__ = 'movimento_caixa'

    id = db.Column(db.Integer, primary_key=True)
    caixa_id = db.Column(db.Integer, db.ForeignKey('caixa.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' ou 'saida'
    categoria = db.Column(db.String(50), nullable=False)  # 'venda', 'compra', 'despesa', 'receita', etc
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    forma_pagamento = db.Column(db.String(50))  # 'dinheiro', 'cartao', 'pix', etc

    def __repr__(self):
        return f'<MovimentoCaixa {self.tipo} - R$ {self.valor}>'

    def to_dict(self):
        return {
            'id': self.id,
            'caixa_id': self.caixa_id,
            'tipo': self.tipo,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'valor': self.valor,
            'data': self.data.isoformat() if self.data else None,
            'forma_pagamento': self.forma_pagamento
        }

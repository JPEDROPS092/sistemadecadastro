from datetime import datetime
from . import db

class Caixa(db.Model):
    __tablename__ = 'caixa'

    id = db.Column(db.Integer, primary_key=True)
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    data_fechamento = db.Column(db.DateTime)
    saldo_inicial = db.Column(db.Float, default=0.0)
    saldo_final = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='aberto')
    observacao = db.Column(db.String(200))
    observacao_abertura = db.Column(db.String(200))
    usuario_abertura_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    movimentos = db.relationship('MovimentoCaixa', backref='caixa', lazy=True, cascade='all, delete-orphan')

    @property
    def total_entradas(self):
        # Calcula a soma em tempo real. Não precisa de setter!
        return sum(m.valor for m in self.movimentos if m.tipo == 'entrada')

    @property
    def total_saidas(self):
        return sum(m.valor for m in self.movimentos if m.tipo == 'saida')

    @property
    def saldo_calculado(self):
        return self.saldo_inicial + self.total_entradas - self.total_saidas
    
    @property
    def saldo_atual(self):
        if self.status == 'fechado':
            return self.saldo_final
        return self.saldo_calculado
    
    @saldo_atual.setter
    def saldo_atual(self, value):
        if self.status != 'fechado':
            self.saldo_inicial = value

    def to_dict(self):
        return {
            'id': self.id,
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'data_fechamento': self.data_fechamento.isoformat() if self.data_fechamento else None,
            'saldo_inicial': self.saldo_inicial,
            'saldo_final': self.saldo_final,
            'saldo_atual': self.saldo_atual,
            'total_entradas': self.total_entradas,
            'total_saidas': self.total_saidas,
            'status': self.status,
            'observacao': self.observacao
        }

class MovimentoCaixa(db.Model):
    __tablename__ = 'movimento_caixa'
    id = db.Column(db.Integer, primary_key=True)
    caixa_id = db.Column(db.Integer, db.ForeignKey('caixa.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    forma_pagamento = db.Column(db.String(50))
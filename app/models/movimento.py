from datetime import datetime
from . import db

class Movimento(db.Model):
    __tablename__ = 'movimento'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' ou 'saida'
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.String(200))

    def __repr__(self):
        return f'<Movimento {self.tipo} - {self.quantidade}>'

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario

    def to_dict(self):
        return {
            'id': self.id,
            'produto_id': self.produto_id,
            'produto_nome': self.produto.nome if self.produto else None,
            'tipo': self.tipo,
            'quantidade': self.quantidade,
            'valor_unitario': self.valor_unitario,
            'valor_total': self.valor_total,
            'data': self.data.isoformat() if self.data else None,
            'observacao': self.observacao
        }

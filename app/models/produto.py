from . import db

class Produto(db.Model):
    __tablename__ = 'produto'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    qtd = db.Column(db.Integer, default=0)
    valor_compra = db.Column(db.Float, nullable=False)
    valor_venda = db.Column(db.Float, nullable=False)
    estoque_minimo = db.Column(db.Integer, default=5)
    ativo = db.Column(db.Boolean, default=True)

    movimentos = db.relationship('Movimento', backref='produto', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Produto {self.nome}>'

    @property
    def quantidade(self):
        """Alias para qtd para compatibilidade"""
        return self.qtd
    
    @quantidade.setter
    def quantidade(self, value):
        """Setter para quantidade"""
        self.qtd = value

    @property
    def estoque_baixo(self):
        return self.qtd <= self.estoque_minimo

    @property
    def margem_lucro(self):
        if self.valor_compra > 0:
            return ((self.valor_venda - self.valor_compra) / self.valor_compra) * 100
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'qtd': self.qtd,
            'quantidade': self.quantidade,  # Adiciona para compatibilidade
            'valor_compra': self.valor_compra,
            'valor_venda': self.valor_venda,
            'estoque_minimo': self.estoque_minimo,
            'estoque_baixo': self.estoque_baixo,
            'margem_lucro': self.margem_lucro,
            'ativo': self.ativo
        }

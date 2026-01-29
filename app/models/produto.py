from . import db

class Produto(db.Model):
    __tablename__ = 'produto'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    qtd = db.Column(db.Integer, default=0)
    valor_compra = db.Column(db.Float, nullable=False, default=0.0)
    valor_venda = db.Column(db.Float, nullable=False, default=0.0)
    estoque_minimo = db.Column(db.Integer, default=5)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamento com Movimentos
    movimentos = db.relationship('Movimento', backref='produto', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Produto {self.nome}>'

    # --- PROPRIEDADES CALCULADAS ---

    @property
    def margem_lucro(self):
        """Calcula a margem de lucro em porcentagem. Única definição necessária."""
        if self.valor_compra and self.valor_compra > 0:
            return ((self.valor_venda - self.valor_compra) / self.valor_compra) * 100
        return 0.0

    @property
    def estoque_baixo(self):
        """Retorna True se o estoque estiver igual ou abaixo do mínimo"""
        return (self.qtd or 0) <= (self.estoque_minimo or 0)

    # --- COMPATIBILIDADE (GETTER/SETTER) ---

    @property
    def quantidade(self):
        """Alias para 'qtd' usado em algumas partes do sistema"""
        return self.qtd
    
    @quantidade.setter
    def quantidade(self, value):
        """Permite definir o valor usando 'quantidade' ou 'qtd'"""
        self.qtd = value

    # --- SERIALIZAÇÃO ---

    def to_dict(self):
        """Converte o objeto para dicionário (útil para JSON/API)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'qtd': self.qtd,
            'quantidade': self.quantidade,
            'valor_compra': self.valor_compra,
            'valor_venda': self.valor_venda,
            'estoque_minimo': self.estoque_minimo,
            'estoque_baixo': self.estoque_baixo,
            'margem_lucro': self.margem_lucro,
            'ativo': self.ativo
        }
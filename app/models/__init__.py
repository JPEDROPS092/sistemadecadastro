from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .produto import Produto
from .movimento import Movimento
from .caixa import Caixa, MovimentoCaixa
from .usuario import Usuario

__all__ = ['db', 'Produto', 'Movimento', 'Caixa', 'MovimentoCaixa', 'Usuario']

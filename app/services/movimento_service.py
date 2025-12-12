from datetime import datetime, timedelta
from app.models import db, Produto, Movimento

class MovimentoService:
    @staticmethod
    def registrar_entrada(produto_id, quantidade, valor_unitario=None, observacao=None):
        produto = Produto.query.get(produto_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        if valor_unitario is None:
            valor_unitario = produto.valor_compra

        produto.qtd += quantidade

        movimento = Movimento(
            produto_id=produto_id,
            tipo='entrada',
            quantidade=quantidade,
            valor_unitario=valor_unitario,
            observacao=observacao
        )

        db.session.add(movimento)
        db.session.commit()
        return movimento

    @staticmethod
    def registrar_saida(produto_id, quantidade, valor_unitario=None, observacao=None):
        produto = Produto.query.get(produto_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        if quantidade > produto.qtd:
            raise ValueError(f"Quantidade insuficiente em estoque. Disponível: {produto.qtd}")

        if valor_unitario is None:
            valor_unitario = produto.valor_venda

        produto.qtd -= quantidade

        movimento = Movimento(
            produto_id=produto_id,
            tipo='saida',
            quantidade=quantidade,
            valor_unitario=valor_unitario,
            observacao=observacao
        )

        db.session.add(movimento)
        db.session.commit()
        return movimento

    @staticmethod
    def listar_movimentos(produto_id=None, tipo=None, data_inicio=None, data_fim=None):
        query = Movimento.query

        if produto_id:
            query = query.filter_by(produto_id=produto_id)

        if tipo:
            query = query.filter_by(tipo=tipo)

        if data_inicio:
            query = query.filter(Movimento.data >= data_inicio)

        if data_fim:
            query = query.filter(Movimento.data <= data_fim)

        return query.order_by(Movimento.data.desc()).all()

    @staticmethod
    def obter_movimento(id):
        return Movimento.query.get(id)

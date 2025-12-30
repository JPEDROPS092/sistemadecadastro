from app.models import db, Produto

class ProdutoService:
    @staticmethod
    def criar_produto(nome, valor_compra, valor_venda, qtd=0, quantidade=None, estoque_minimo=5):
        # Aceitar 'quantidade' como alias para 'qtd'
        if quantidade is not None:
            qtd = quantidade
            
        produto = Produto(
            nome=nome,
            valor_compra=valor_compra,
            valor_venda=valor_venda,
            qtd=qtd,
            estoque_minimo=estoque_minimo
        )
        db.session.add(produto)
        db.session.commit()
        return produto

    @staticmethod
    def listar_produtos(incluir_inativos=False):
        if incluir_inativos:
            return Produto.query.all()
        return Produto.query.filter_by(ativo=True).all()

    @staticmethod
    def obter_produto(id):
        return Produto.query.get(id)

    @staticmethod
    def atualizar_produto(id, **kwargs):
        produto = Produto.query.get(id)
        if not produto:
            return None

        for key, value in kwargs.items():
            if hasattr(produto, key):
                setattr(produto, key, value)

        db.session.commit()
        return produto

    @staticmethod
    def excluir_produto(id):
        produto = Produto.query.get(id)
        if produto:
            # Verifica se há movimentos associados
            if produto.movimentos:
                # Se há movimentos, apenas marca como inativo
                produto.ativo = False
                db.session.commit()
                return True
            else:
                # Se não há movimentos, pode excluir fisicamente
                db.session.delete(produto)
                db.session.commit()
                return True
        return False

    @staticmethod
    def atualizar_estoque(id, quantidade_alteracao):
        produto = Produto.query.get(id)
        if produto:
            produto.qtd += quantidade_alteracao
            db.session.commit()
            return produto
        return None

    @staticmethod
    def produtos_estoque_baixo():
        return Produto.query.filter(Produto.qtd <= Produto.estoque_minimo, Produto.ativo == True).all()

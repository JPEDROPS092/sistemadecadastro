from app.models import db, Produto

class ProdutoService:
    @staticmethod
    def criar_produto(nome, valor_compra, valor_venda, qtd=0, quantidade=None, estoque_minimo=5):
        """Cria um novo produto com validação rigorosa de tipos."""
        try:
            # Consolida a lógica de quantidade inicial
            estoque_inicial = int(quantidade if quantidade is not None else qtd)
            
            produto = Produto(
                nome=nome.strip(), # Remove espaços extras
                valor_compra=float(valor_compra or 0), 
                valor_venda=float(valor_venda or 0),   
                qtd=estoque_inicial,
                estoque_minimo=int(estoque_minimo or 5),
                ativo=True
            )
            
            db.session.add(produto)
            db.session.commit()
            return produto
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def listar_produtos(incluir_inativos=False):
        """Retorna a lista de produtos ordenada alfabeticamente."""
        query = Produto.query
        if not incluir_inativos:
            query = query.filter_by(ativo=True)
        return query.order_by(Produto.nome.asc()).all()

    @staticmethod
    def obter_produto(id):
        """Busca um produto pelo ID (Primary Key)."""
        return Produto.query.get(id)

    @staticmethod
    def atualizar_produto(id, **kwargs):
        """Atualiza campos dinamicamente garantindo a integridade dos tipos."""
        produto = Produto.query.get(id)
        if not produto:
            return None

        try:
            for key, value in kwargs.items():
                if hasattr(produto, key) and value is not None:
                    # Conversão forçada de tipos para segurança do banco
                    if key in ['valor_compra', 'valor_venda']:
                        value = float(value)
                    elif key in ['qtd', 'estoque_minimo']:
                        value = int(value)
                    
                    setattr(produto, key, value)

            db.session.commit()
            return produto
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def excluir_produto(id):
        """Inativa o produto (Soft Delete) para preservar o histórico financeiro."""
        produto = Produto.query.get(id)
        if produto:
            try:
                # IMPORTANTE: Em sistemas comerciais, quase nunca excluímos 
                # fisicamente um produto para não quebrar relatórios de vendas antigos.
                produto.ativo = False 
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise e
        return False

    @staticmethod
    def atualizar_estoque(id, quantidade_alteracao):
        """
        Altera o saldo de estoque. 
        Sempre prefira usar o MovimentoService para chamadas externas 
        para manter o log de auditoria.
        """
        produto = Produto.query.get(id)
        if produto:
            try:
                produto.qtd = (produto.qtd or 0) + int(quantidade_alteracao)
                db.session.commit()
                return produto
            except Exception as e:
                db.session.rollback()
                raise e
        return None

    @staticmethod
    def produtos_estoque_baixo():
        """Filtra produtos ativos que atingiram o limite crítico definido."""
        return Produto.query.filter(
            Produto.ativo == True,
            Produto.qtd <= Produto.estoque_minimo
        ).order_by(Produto.qtd.asc()).all()
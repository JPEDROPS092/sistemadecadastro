from datetime import datetime
from app.models import db, Produto, Movimento

class MovimentoService:
    @staticmethod
    def registrar_entrada(produto_id, quantidade, valor_unitario=None, motivo="Entrada manual"):
        """Registra a entrada de produtos no estoque sincronizando com o banco."""
        produto = Produto.query.get(produto_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        try:
            # Sincroniza o saldo atual para evitar erros de cálculo
            db.session.refresh(produto)

            qtd_int = int(quantidade)
            if qtd_int <= 0:
                raise ValueError("A quantidade deve ser maior que zero")

            # Tratamento de valor unitário (usa custo do cadastro se vazio)
            if valor_unitario is None or (isinstance(valor_unitario, str) and not str(valor_unitario).strip()):
                v_unitario = float(produto.valor_custo or 0)
            else:
                v_unitario = float(str(valor_unitario).replace(',', '.'))

            # Atualiza o estoque (o commit será feito pelo Blueprint/Rota)
            produto.qtd = (produto.qtd or 0) + qtd_int

            movimento = Movimento(
                produto_id=produto_id,
                tipo='entrada',
                quantidade=qtd_int,
                valor_unitario=v_unitario,
                motivo=str(motivo),
                data=datetime.now()
            )

            db.session.add(movimento)
            return movimento
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def registrar_saida(produto_id, quantidade, valor_unitario=None, motivo="Saída"):
        """Registra a saída sem subtrair novamente para evitar baixa duplicada."""
        produto = Produto.query.get(produto_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        try:
            qtd_int = int(quantidade)
            v_unitario = float(valor_unitario) if valor_unitario and not isinstance(valor_unitario, str) else float(produto.valor_venda or 0)

            movimento = Movimento(
                produto_id=produto_id,
                tipo='saida',
                quantidade=qtd_int,
                valor_unitario=v_unitario,
                motivo=str(motivo),
                data=datetime.now()
            )
            db.session.add(movimento)
            return movimento
        except Exception as e:
            raise e

    @staticmethod
    def listar_movimentos(produto_id=None, tipo=None, data_inicio=None, data_fim=None, limite=100):
        """Lista os movimentos aplicando filtros de data e tipo."""
        query = Movimento.query
        if produto_id:
            query = query.filter(Movimento.produto_id == produto_id)
        if tipo:
            query = query.filter(Movimento.tipo.ilike(f"%{tipo}%"))
        if data_inicio:
            query = query.filter(Movimento.data >= data_inicio)
        if data_fim:
            query = query.filter(Movimento.data <= data_fim)
        
        return query.order_by(Movimento.id.desc()).limit(limite).all()
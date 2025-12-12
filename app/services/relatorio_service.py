from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import db, Produto, Movimento, Caixa, MovimentoCaixa

class RelatorioService:
    @staticmethod
    def relatorio_estoque():
        produtos = Produto.query.filter_by(ativo=True).all()

        total_valor_estoque = sum(p.qtd * p.valor_compra for p in produtos)
        total_valor_venda = sum(p.qtd * p.valor_venda for p in produtos)
        produtos_estoque_baixo = [p for p in produtos if p.estoque_baixo]

        return {
            'produtos': [p.to_dict() for p in produtos],
            'total_valor_estoque': total_valor_estoque,
            'total_valor_venda': total_valor_venda,
            'lucro_potencial': total_valor_venda - total_valor_estoque,
            'produtos_estoque_baixo': len(produtos_estoque_baixo)
        }

    @staticmethod
    def relatorio_movimentos(data_inicio=None, data_fim=None):
        if not data_inicio:
            data_inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        if not data_fim:
            data_fim = datetime.utcnow()

        movimentos = Movimento.query.filter(
            Movimento.data >= data_inicio,
            Movimento.data <= data_fim
        ).all()

        entradas = [m for m in movimentos if m.tipo == 'entrada']
        saidas = [m for m in movimentos if m.tipo == 'saida']

        total_entradas = sum(m.valor_total for m in entradas)
        total_saidas = sum(m.valor_total for m in saidas)

        return {
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat(),
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'lucro': total_saidas - total_entradas,
            'quantidade_entradas': sum(m.quantidade for m in entradas),
            'quantidade_saidas': sum(m.quantidade for m in saidas),
            'movimentos': [m.to_dict() for m in movimentos]
        }

    @staticmethod
    def relatorio_diario():
        hoje = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        amanha = hoje + timedelta(days=1)
        return RelatorioService.relatorio_movimentos(hoje, amanha)

    @staticmethod
    def relatorio_semanal():
        hoje = datetime.utcnow()
        semana_atras = hoje - timedelta(days=7)
        return RelatorioService.relatorio_movimentos(semana_atras, hoje)

    @staticmethod
    def relatorio_mensal():
        hoje = datetime.utcnow()
        mes_atras = hoje - timedelta(days=30)
        return RelatorioService.relatorio_movimentos(mes_atras, hoje)

    @staticmethod
    def relatorio_caixa(caixa_id=None):
        if caixa_id:
            caixa = Caixa.query.get(caixa_id)
            if not caixa:
                return None
            return caixa.to_dict()
        else:
            caixa_aberto = Caixa.query.filter_by(status='aberto').first()
            if caixa_aberto:
                return caixa_aberto.to_dict()
            return None

    @staticmethod
    def relatorio_fluxo_diario():
        hoje = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Movimentos de estoque
        movimentos_estoque = Movimento.query.filter(Movimento.data >= hoje).all()

        # Movimentos de caixa
        caixa_aberto = Caixa.query.filter_by(status='aberto').first()
        movimentos_caixa = []
        if caixa_aberto:
            movimentos_caixa = MovimentoCaixa.query.filter(
                MovimentoCaixa.caixa_id == caixa_aberto.id,
                MovimentoCaixa.data >= hoje
            ).all()

        total_vendas = sum(m.valor_total for m in movimentos_estoque if m.tipo == 'saida')
        total_compras = sum(m.valor_total for m in movimentos_estoque if m.tipo == 'entrada')

        total_entradas_caixa = sum(m.valor for m in movimentos_caixa if m.tipo == 'entrada')
        total_saidas_caixa = sum(m.valor for m in movimentos_caixa if m.tipo == 'saida')

        return {
            'data': hoje.isoformat(),
            'vendas': total_vendas,
            'compras': total_compras,
            'lucro_bruto': total_vendas - total_compras,
            'entradas_caixa': total_entradas_caixa,
            'saidas_caixa': total_saidas_caixa,
            'saldo_caixa': total_entradas_caixa - total_saidas_caixa,
            'movimentos_estoque': [m.to_dict() for m in movimentos_estoque],
            'movimentos_caixa': [m.to_dict() for m in movimentos_caixa]
        }

    @staticmethod
    def dashboard():
        hoje = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Estatísticas gerais
        total_produtos = Produto.query.filter_by(ativo=True).count()
        produtos_estoque_baixo = Produto.query.filter(
            Produto.qtd <= Produto.estoque_minimo,
            Produto.ativo == True
        ).count()

        # Movimentos do dia
        movimentos_hoje = Movimento.query.filter(Movimento.data >= hoje).all()
        vendas_hoje = sum(m.valor_total for m in movimentos_hoje if m.tipo == 'saida')
        compras_hoje = sum(m.valor_total for m in movimentos_hoje if m.tipo == 'entrada')

        # Caixa
        caixa_aberto = Caixa.query.filter_by(status='aberto').first()
        saldo_caixa = caixa_aberto.saldo_calculado if caixa_aberto else 0

        # Produtos mais vendidos (últimos 7 dias)
        semana_atras = hoje - timedelta(days=7)
        produtos_mais_vendidos = db.session.query(
            Produto.nome,
            func.sum(Movimento.quantidade).label('total')
        ).join(Movimento).filter(
            Movimento.tipo == 'saida',
            Movimento.data >= semana_atras
        ).group_by(Produto.id).order_by(func.sum(Movimento.quantidade).desc()).limit(5).all()

        return {
            'total_produtos': total_produtos,
            'produtos_estoque_baixo': produtos_estoque_baixo,
            'vendas_hoje': vendas_hoje,
            'compras_hoje': compras_hoje,
            'lucro_hoje': vendas_hoje - compras_hoje,
            'saldo_caixa': saldo_caixa,
            'caixa_status': caixa_aberto.status if caixa_aberto else 'fechado',
            'produtos_mais_vendidos': [{'nome': p[0], 'quantidade': p[1]} for p in produtos_mais_vendidos]
        }

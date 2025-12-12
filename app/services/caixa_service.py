from datetime import datetime
from app.models import db, Caixa, MovimentoCaixa

class CaixaService:
    @staticmethod
    def abrir_caixa(saldo_inicial=0.0, observacao=None):
        caixa_aberto = Caixa.query.filter_by(status='aberto').first()
        if caixa_aberto:
            raise ValueError("Já existe um caixa aberto")

        caixa = Caixa(
            saldo_inicial=saldo_inicial,
            saldo_final=saldo_inicial,
            observacao=observacao
        )
        db.session.add(caixa)
        db.session.commit()
        return caixa

    @staticmethod
    def fechar_caixa(caixa_id, observacao=None):
        caixa = Caixa.query.get(caixa_id)
        if not caixa:
            raise ValueError("Caixa não encontrado")

        if caixa.status == 'fechado':
            raise ValueError("Caixa já está fechado")

        caixa.status = 'fechado'
        caixa.data_fechamento = datetime.utcnow()
        caixa.saldo_final = caixa.saldo_calculado
        if observacao:
            caixa.observacao = observacao

        db.session.commit()
        return caixa

    @staticmethod
    def obter_caixa_aberto():
        return Caixa.query.filter_by(status='aberto').first()

    @staticmethod
    def obter_caixa(id):
        return Caixa.query.get(id)

    @staticmethod
    def listar_caixas(data_inicio=None, data_fim=None):
        query = Caixa.query

        if data_inicio:
            query = query.filter(Caixa.data_abertura >= data_inicio)

        if data_fim:
            query = query.filter(Caixa.data_abertura <= data_fim)

        return query.order_by(Caixa.data_abertura.desc()).all()

    @staticmethod
    def registrar_movimento(caixa_id, tipo, categoria, descricao, valor, forma_pagamento=None):
        caixa = Caixa.query.get(caixa_id)
        if not caixa:
            raise ValueError("Caixa não encontrado")

        if caixa.status != 'aberto':
            raise ValueError("Caixa está fechado")

        movimento = MovimentoCaixa(
            caixa_id=caixa_id,
            tipo=tipo,
            categoria=categoria,
            descricao=descricao,
            valor=valor,
            forma_pagamento=forma_pagamento
        )

        db.session.add(movimento)
        db.session.commit()
        return movimento

    @staticmethod
    def listar_movimentos_caixa(caixa_id):
        return MovimentoCaixa.query.filter_by(caixa_id=caixa_id).order_by(MovimentoCaixa.data.desc()).all()

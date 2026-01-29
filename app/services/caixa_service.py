from datetime import datetime
from app.models import db, Caixa, MovimentoCaixa, Movimento

class CaixaService:
    @staticmethod
    def abrir_caixa(saldo_inicial=0.0, observacao_abertura=None):
        """Abre um novo turno de caixa se não houver um aberto."""
        caixa_aberto = CaixaService.obter_caixa_aberto()
        if caixa_aberto:
            raise ValueError("Já existe um caixa aberto")

        # As propriedades total_entradas e total_saidas são calculadas automaticamente no Model.
        caixa = Caixa(
            saldo_inicial=float(saldo_inicial),
            status='aberto',
            observacao_abertura=observacao_abertura,
            data_abertura=datetime.utcnow()
        )
        db.session.add(caixa)
        db.session.commit()
        return caixa

    @staticmethod
    def registrar_venda(caixa_id, valor, forma_pagamento):
        """Converte uma venda finalizada em um movimento financeiro."""
        return CaixaService.registrar_movimento(
            caixa_id=caixa_id,
            tipo='entrada',
            categoria='venda',
            descricao=f'Venda PDV - {forma_pagamento}',
            valor=valor,
            forma_pagamento=forma_pagamento
        )

    @staticmethod
    def registrar_movimento(caixa_id, tipo, categoria, descricao, valor, forma_pagamento=None):
        """Registra qualquer entrada ou saída financeira no caixa aberto."""
        caixa = Caixa.query.get(caixa_id)
        if not caixa or caixa.status != 'aberto':
            raise ValueError("Caixa não encontrado ou fechado")

        movimento = MovimentoCaixa(
            caixa_id=caixa_id,
            tipo=tipo,
            categoria=categoria,
            descricao=descricao,
            valor=float(valor),
            forma_pagamento=forma_pagamento,
            data=datetime.utcnow()
        )
        
        db.session.add(movimento)
        # O commit é controlado pela rota para garantir integridade total.
        return movimento

    @staticmethod
    def fechar_caixa(caixa_id, observacao=None):
        """Encerra o turno do caixa e congela o saldo final para histórico."""
        caixa = Caixa.query.get(caixa_id)
        if not caixa or caixa.status == 'fechado':
            raise ValueError("Caixa inválido ou já encerrado")

        caixa.saldo_final = caixa.saldo_calculado # Salva o estado atual
        caixa.status = 'fechado'
        caixa.data_fechamento = datetime.utcnow()
        caixa.observacao = observacao
        
        db.session.commit()
        return caixa

    @staticmethod
    def obter_caixa_aberto():
        """MÉTODO QUE ESTAVA FALTANDO: Retorna o caixa com status 'aberto'."""
        return Caixa.query.filter_by(status='aberto').first()

    @staticmethod
    def listar_movimentos_caixa(caixa_id):
        """Retorna o histórico de operações do turno atual."""
        return MovimentoCaixa.query.filter_by(caixa_id=caixa_id).order_by(MovimentoCaixa.data.desc()).all()
    @staticmethod
    def listar_historico_fechamentos():
       from app.models import Movimento # Importação interna para evitar conflitos
       return Movimento.query.order_by(Movimento.id.desc()).all()
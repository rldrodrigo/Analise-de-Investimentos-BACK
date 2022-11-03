
class TesouroModel:
    def __init__(self, tipo_titulo, vencimento, data_venda, pu, quantidade, valor):
        self.tipo_titulo = tipo_titulo
        self.vencimento = vencimento
        self.data_venda = data_venda
        self.pu = pu
        self.quantidade = quantidade
        self.valor = valor

    def json(self):
        return {
            'tipo_titulo' = self.tipo_titulo,
            'vencimento' = self.vencimento,
            'data_venda' = self.data_venda,
            'pu' = self.pu,
            'quantidade' = self.quantidade,
            'valor' = self.valor,
        }
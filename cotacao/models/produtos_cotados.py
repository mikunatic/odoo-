from odoo import fields, models


class ProdutosCotados(models.Model):
    _name = 'produtos.cotados'
    _inherits = {"product.product": "product_id"}


    quantidade_a_levar = fields.Float("Quantidade à Levar")
    product_id = fields.Many2one('product.product')
    custo = fields.Float(related="product_id.standard_price")
    cotacao_id = fields.Many2one('cotacao')
    pre_pedido = fields.Boolean("Pré-Pedido")
    qty_available = fields.Float(related="product_id.qty_available")
    valor_total = fields.Float("Valor Total", compute="calcula_valor_total")

    def calcula_valor_total(self):
        for rec in self:
            resultado = rec.quantidade_a_levar * rec.custo
            rec.valor_total = resultado
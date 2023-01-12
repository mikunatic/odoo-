from odoo import fields, models,api


class LoteInherit(models.Model):
    _inherit = 'lote.cheque'

    cheque_ids = fields.Many2many('cadastro.cheque', domain="[('pagamentos','=',False)]")
    currency_id = fields.Many2one('res.currency', default=6)
    valor_total = fields.Monetary(currency_field='currency_id', compute="calculartotal")

    @api.depends("cheque_ids")
    def calculartotal(self):
        valor = 0
        for lote in self:
            for cheque in lote.cheque_ids:
                valor += cheque.valor
            lote.valor_total = valor
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cotacao = fields.Many2one('cotacao')
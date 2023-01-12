from odoo import fields, models


class LoteCheque(models.Model):
    _name = 'lote.cheque'

    numero_lote = fields.Char("Número do Lote", required=True)


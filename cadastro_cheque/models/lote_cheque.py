from odoo import fields, models


class LoteCheque(models.Model):
    _name = 'lote.cheque'
    _rec_name = 'numero_lote'

    numero_lote = fields.Char("Número do Lote", required=True)


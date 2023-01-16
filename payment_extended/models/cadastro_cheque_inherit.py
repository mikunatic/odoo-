from odoo import fields, models


class ChequeInherit(models.Model):
    _inherit = 'cadastro.cheque'

    pagamentos = fields.One2many(comodel_name='account.payment', inverse_name='cheque_pagamento', readonly=True)
    gerproc_id = fields.Many2one('project_request')
    lote_ids = fields.Many2many('lote.cheque', string="Lote pertencente")
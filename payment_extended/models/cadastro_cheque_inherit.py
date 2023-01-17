from odoo import fields, models, api


class ChequeInherit(models.Model):
    _inherit = 'cadastro.cheque'

    pagamentos = fields.One2many(comodel_name='account.payment', inverse_name='cheque_pagamento', readonly=True)
    gerproc_id = fields.Many2one('project_request', readonly=True, string="GerProc feito na criação do cheque")
    lote_ids = fields.Many2many('lote.cheque', string="Lote pertencente")
    cadastro_cheque_ids = fields.One2many(comodel_name='account.payment', inverse_name='cadastro_cheque', readonly=True, string="Movimentos da criação do cheque")

    @api.depends("pagamentos")
    def cheque(self):
        if self.pagamentos:
            self.lote_ids = False
        return
from odoo import fields, models


class PaymentInherit(models.Model):
    _inherit = 'account.payment'

    gerproc = fields.Many2one('project_request')
    effective_date = fields.Char("effective_date")
    bank_reference = fields.Char("bank_reference")
    cheque_reference = fields.Char("cheque_reference")
    # forma_pagamento = fields.Selection([('1','Dinheiro'),('2','Cheque')])
    # cheque = fields.Many2one('cadastro.cheque', string="Cheque")
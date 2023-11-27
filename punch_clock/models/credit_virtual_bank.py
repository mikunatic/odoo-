from odoo import fields, models, api


class CreditVirtualBank(models.Model):
    _name = 'credit.virtual.bank'
    _rec_name = 'credit_name'

    credit_name = fields.Char('evento')

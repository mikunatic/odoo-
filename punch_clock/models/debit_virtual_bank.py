from odoo import fields, models, api


class CreditVirtualBank(models.Model):
    _name = 'debit.virtual.bank'
    _rec_name = 'debit_name'

    debit_name = fields.Char('evento')

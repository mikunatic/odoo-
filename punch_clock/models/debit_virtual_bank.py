from odoo import fields, models


class DebitVirtualBank(models.Model):
    _name = 'debit.virtual.bank'

    name = fields.Char("Nome")
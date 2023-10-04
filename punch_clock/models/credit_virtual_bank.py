from odoo import fields, models


class CreditVirtualBank(models.Model):
    _name = 'credit.virtual.bank'

    name = fields.Char("Nome")
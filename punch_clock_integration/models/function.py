from odoo import fields, models


class Function(models.Model):
    _name = 'function'

    name = fields.Char()
from odoo import fields, models


class Hour(models.Model):
    _name = 'hour'
    _rec_name = 'time'

    time = fields.Char()
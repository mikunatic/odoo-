from odoo import fields, models


class WeekDays(models.Model):
    _name = 'week.days'
    _rec_name = 'day'

    day = fields.Char(string="Dia")

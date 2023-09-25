from odoo import fields, models, api


class JustificationHolidays(models.Model):
    _name = 'justification.holidays'
    _rec_name = 'event'

    data = fields.Char(string='Data')
    event = fields.Char(string='Evento')
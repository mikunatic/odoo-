from odoo import fields, models


class Workday(models.Model):
    _name = 'workday'

    entrance_hour = fields.Many2one('hour', string="Hora de Entrada")
    departure_hour = fields.Many2one('hour', string="Hora de Saída")
    week_days_id = fields.Many2one('week.days', string="Dias da semana")
    employee_id = fields.Many2one('hr.employee')
    intraday = fields.Integer("Intrajornada")
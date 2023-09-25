from odoo import fields, models


class Intraday(models.Model):
    _name = 'intraday'

    employee_id = fields.Many2one('hr.employee', "Funcionário")
    hour_minute_selection = fields.Selection([('hour','Hora'),('minute','Minuto')], string="Hora/Minuto")
    value = fields.Integer("Valor")
from odoo import api, fields, models


class Holiday(models.Model):
    _name = 'holiday'

    name = fields.Char()
    description = fields.Char()
    employees_ids = fields.Many2many('hr.employee')
    inicial_date = fields.Date()
    final_date = fields.Date()
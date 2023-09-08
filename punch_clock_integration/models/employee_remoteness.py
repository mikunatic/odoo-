from odoo import fields, models


class EmployeeRemoteness(models.Model):
    _name = 'employee.remoteness'
    _rec_name = 'reason'

    reason = fields.Many2one('remoteness')
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    initial_date = fields.Date(string="Data inicial")
    final_date = fields.Date(string="Data final")
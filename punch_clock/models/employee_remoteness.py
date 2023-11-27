from odoo import fields, models


class EmployeeRemoteness(models.Model):
    _name = 'employee.remoteness'
    _rec_name = 'reason'

    reason = fields.Many2one('remoteness', required=True, string="Motivo do Afastamento")
    employee_remoteness_ids = fields.Many2many('hr.employee', required=True, string="Funcionários")
    initial_date = fields.Date(string="Data inicial", required=True)
    final_date = fields.Date(string="Data final", required=True)
    remuneration = fields.Boolean(related='reason.remuneration', string='Remuneração')
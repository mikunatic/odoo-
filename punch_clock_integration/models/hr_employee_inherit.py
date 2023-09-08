from odoo import fields, models, api
from datetime import timedelta


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    employee_pis = fields.Char(string="PIS")
    company = fields.Many2one('employee.company',string="Empresa")
    function_id = fields.Many2one('function', string="Função")
    workday_ids = fields.One2many(comodel_name='workday', inverse_name='employee_id', string="Jornada de trabalho")
    overnight_stay = fields.Boolean("Pernoite")
    syndicate_id = fields.Many2one('syndicate', string='Sindicato')

    def name_get(self):
        return [(rec.id, rec.name + " (demitido)" if rec.employee_pis[0] == "d" else rec.name) for rec in self]

    # virtual_time = fields.Float(string="Horas virtuais", compute="compute_virtual_time")
    #
    # def compute_virtual_time(self):
    #     punchs_of_employee = self.env['punch.clock'].search([('employee_pis', '=', '13499969938')])
    #
    #     punchs_days_of_employee = punchs_of_employee.mapped('punch_datetime')
    #     self.virtual_time = 0
    #     for day in punchs_days_of_employee:
    #         day = day.replace(hour=0, minute=0, second=0, microsecond=0)
    #         punchs_of_employee = self.env['punch.clock'].search(
    #         [('employee_pis', '=', '13499969938'), ('punch_datetime', '<', day + timedelta(days=1)),
    #          ('punch_datetime', '>', day + timedelta(days=-1))])
    #     mod_punchs = punchs_of_employee % 2
    #     if mod_punchs == 0:
             # verificar se tem batida de ponto par... ou seja se ele teve entyrada e saida
import datetime

from odoo import fields, models, api
from datetime import timedelta


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    employee_pis = fields.Char(string="PIS")
    company_id = fields.Many2one('employee.company',string="Empresa")
    function_id = fields.Many2one('function', string="Função")
    workday_ids = fields.One2many(comodel_name='workday', inverse_name='employee_id', string="Jornada de trabalho")
    overnight_stay = fields.Boolean("Pernoite")
    syndicate_id = fields.Many2one('syndicate', string='Sindicato')
    intraday = fields.One2many('intraday', 'employee_id', string="Intrajornada")
    paid_weekly_rest = fields.Many2one('week.days', string="Repouso Semanal Remunerado")

    def name_get(self):# não ta aplicando
        return [(rec.id, rec.name + " (demitido)" if rec.employee_pis[0] == "d" else rec.name) for rec in self]
        # result = []
        # for rec in self:
        #     if rec.employee_pis:
        #         name = "{} - DEMITIDO".format(rec.name) if rec.employee_pis.split(' ')[0].__eq__("d") else rec.name
        #     result.append((rec.id, name))
        # return result

    # virtual_seconds = fields.Integer(compute="compute_virtual_seconds")
    # virtual_time = fields.Char(string="Horas virtuais", compute="compute_virtual_time")

    @api.depends('virtual_seconds')
    def compute_virtual_time(self):#Função que transforma o campo integer de segundos bonus, para um char legível de horas
        self.virtual_time = str(self.virtual_seconds // 3600) + ":" + str((self.virtual_seconds % 3600) // 60)


    #ver forma de criar a função que calcula os segundos virtuais aqui
    # def compute_virtual_seconds(self):
    #     now = datetime.date.today()
    #     last_year = now - timedelta(days=365)
    #     days_range = (now - last_year).days
    #     i = last_year
    #     punch_ids = self.env['punch.clock'].search([('employee_id','=',self.id),('punch_datetime','<=',now),('punch_datetime','>=',last_year)])
    #     for day in range(days_range):
    #         employee_punch_ids = punch_ids.filtered(lambda lm: lm.punch_datetime.date() == i)
    #         i += timedelta(days=1)
    #         print("a")
    #         # punch_ids = self.env['punch.clock'].search([('employee_id','=',self.id),('punch_datetime','<=',now),('punch_datetime','>=',last_year)])
    #     print("a")

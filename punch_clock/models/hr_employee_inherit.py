from odoo import fields, models, api
import datetime


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    employee_pis = fields.Char(string="PIS")
    # company_id = fields.Many2one('employee.company', string="Empresa")
    function_id = fields.Many2one('function', string="Função")
    workday_id = fields.One2many('workday', 'employee_id', string="Jornada de trabalho")
    overnight_stay = fields.Boolean("Pernoite")
    syndicate_id = fields.Many2one('syndicate', string='Sindicato')
    week_days_ids = fields.Many2many('week.days', string='Dias trabalhados')
    event_ids = fields.Many2many('event', string="Eventos")
    general_configuration_id = fields.Many2one('general.configuration')
    # virtual_time = fields.Char(compute='compute_virtual_time')
    # extra_hour_lunch = fields.Char()
    dsr_week_days_id = fields.Many2one('week.days', string='DSR')
    virtual_bank_ids = fields.One2many('virtual.bank','employee_id', string="Banco Virtual")
    bonus_hours = fields.Char("Horas Bônus", compute="_compute_bonus_hours")

    def _compute_bonus_hours(self):
        seconds = 0
        for line in self.virtual_bank_ids:
            seconds += line.seconds

    def name_get(self):# rec_name para diferenciar os funcionários demitidos dos admitidos
        return [(rec.id, rec.name + " (demitido)" if rec.employee_pis[0] == "d" else rec.name) for rec in self]

    #FAZER FIELD ONDE ELE CALCULA O SALDO FINAL DE HORAS PARA O FUNCIONÁRIO
    #FOR PELAS LINHAS DO VIRTUAL BANK, SE FOR CREDIT, SOMA, ELSE, SUBTRAI
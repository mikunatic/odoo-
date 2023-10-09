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
    dsr_week_days_id = fields.Many2one('week.days', string='DSR')

    def open_virtual_bank(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Banco Virtual',
            'view_mode': 'tree,form',
            'res_model': 'virtual.bank',
            'domain': [('employee_id','=',self.env['hr.employee'].browse(self.id).id)],
            'context': self.env.context,
            'target': 'current'
        }

    def name_get(self):# rec_name para diferenciar os funcionários demitidos dos admitidos
        return [(rec.id, rec.name + " (demitido)" if rec.employee_pis[0] == "d" else rec.name) for rec in self]
from odoo import fields, models, api
from datetime import timedelta
from datetime import date
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
    # extract_virtual_hours = fields.One2many('extract.virtual.hours','employee_id', compute="compute_extract")

    def name_get(self):# rec_name para diferenciar os funcionários demitidos dos admitidos
        return [(rec.id, rec.name + " (demitido)" if rec.employee_pis[0] == "d" else rec.name) for rec in self]

    def load_virtual_bank(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Banco Virtual',
            'view_mode': 'tree,form',
            'res_model': 'extract.virtual.hours',
            'domain': [('employee_id', '=', self.id)],
            'target': 'current'
        }

    # def deltatime_to_hours_minutes(self, deltatime):
    #     total_minutes_work = deltatime.days * 24 * 60 + deltatime.seconds // 60
    #     hours_work = total_minutes_work // 60
    #     minutes_work = total_minutes_work % 60
    #     return hours_work, minutes_work
    # #
    # def compute_extract(self):
    #     timedelta_extra_hour_lunch = timedelta()
    #     one_year_ago = date.today() - datetime.timedelta(days=30)
    #     punch_clock = self.env['punch.clock'].search(
    #         [('employee_pis', '=', self.employee_pis), ('punch_date', '>=', one_year_ago)])
    #
    #     for rec in punch_clock:
    #         vals = {
    #         'time': 'este campo sera modificado',
    #         'day':rec.punch_date,
    #         'employee_id': self.id,
    #         'hour_move_id': 'este campo sera modificado',
    #         }
    #         format_excess = self.deltatime_to_hours_minutes(rec.compute_extra_hour())
    #         print(rec)
    #
    #         vals['time'] = rec.extra_hour = "{:02d}:{:02d}".format(format_excess[0], format_excess[1])
    #         vals['hour_move_id'] = self.env['hour.move'].search([('name','=','Hora excedente'),('operation_type','=','credito')]).id

            # timedelta_extra_hour_lunch += rec.compute_lunch_time()
            # self.env['extract.virtual.hours'].create(vals)
            # self.extract_virtual_hours = self.extract_virtual_hours
        # format_overtime = self.deltatime_to_hours_minutes(timedelta_overtime)
        # self.virtual_time = "{:02d}:{:02d}".format(format_overtime[0], format_overtime[1])
        #
        # format_extra_hour_lunch = self.deltatime_to_hours_minutes(timedelta_extra_hour_lunch)
        # self.extra_hour_lunch = "{:02d}:{:02d}".format(format_extra_hour_lunch[0], format_extra_hour_lunch[1])

from odoo import models, fields, api,_
from datetime import datetime, timedelta
from odoo.exceptions import Warning


class PunchTime(models.TransientModel):
    _name = 'punch.time'

    manage_employee_time_id = fields.Many2one('manage.employee.time')
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    punch_clock_ids = fields.Many2many('punch.clock', string="Batidas")
    employee_pis = fields.Char(string="PIS do Funcionário")
    date = fields.Date(string="Dia")
    daily_hours = fields.Char(string="Horas trabalhadas", compute='calculate_daily_hours')
    week_day = fields.Char("Dia da Semana")
    should_work = fields.Boolean()
    remoteness_id = fields.Many2one('remoteness', string="Justificativa")
    justification_id = fields.Many2one('justification')
    button_attrs_bool = fields.Boolean(compute="_attrs_bool_compute")
    divergent_punchs = fields.Boolean()

    def _attrs_bool_compute(self):
        if self.remoteness_id.id == 26 and not self.justification_id:
            button_attrs_bool = True
        else:
            button_attrs_bool = False
        self.button_attrs_bool = button_attrs_bool

    def calculate_daily_hours(self):
        for rec in self:
            first = rec.punch_clock_ids[0].punch_datetime if rec.punch_clock_ids else 0
            last = rec.punch_clock_ids[-1].punch_datetime if rec.punch_clock_ids else 0
            diference = (last) - (first)
            if len(rec.punch_clock_ids) >= 4:
                intraday = (rec.punch_clock_ids[2].punch_datetime) - (rec.punch_clock_ids[1].punch_datetime)
                diference -= intraday
            if rec.punch_clock_ids:
                horas = diference.seconds // 3600
                minutos = (diference.seconds % 3600) // 60
            rec.daily_hours = str(horas) + ":" + str(minutos) if rec.punch_clock_ids else "0:0"

    def add_punch(self):
        ctx = dict()
        ctx.update({
            'default_manage_employee_time_id': self.manage_employee_time_id.id,
            'default_date': self.date,
            'default_employee_id': self.employee_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ponto Manual',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manual.point',
            'views': [[self.env.ref("punch_clock_integration.manual_point_form_view").id, 'form']],
            'context': ctx,
            'target': 'new',
        }

    def add_justification(self):
        ctx = dict()
        ctx.update({
            'default_manage_employee_time_id': self.manage_employee_time_id.id,
            'default_first_day': self.date,
            'default_last_day': self.date,
            'default_employee_id': self.employee_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Adicionar Justificativa',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.justification',
            'views': [[self.env.ref("punch_clock_integration.add_justification_form_view").id, 'form']],
            'context': ctx,
            'target': 'new',
        }
from odoo import models, fields, api


class PunchTime(models.TransientModel):
    _name = 'punch.time'

    manage_employee_time_id = fields.Many2one('manage.employee.time')
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    punch_clock_ids = fields.Many2many('punch.clock', string="Batidas")
    employee_pis = fields.Char(string="PIS do Funcionário")
    date = fields.Date(string="Dia")
    daily_hours = fields.Char(string="Horas trabalhadas", compute="calculate_daily_hours")
    week_day = fields.Char("Dia da Semana")
    should_work = fields.Boolean()
    justification_id = fields.Many2one('justification', string="Justificativa")

    def calculate_daily_hours(self):
        first = self.punch_clock_ids[0].punch_datetime if self.punch_clock_ids else 0
        last = self.punch_clock_ids[-1].punch_datetime if self.punch_clock_ids else 0
        diference = (last) - (first)
        if len(self.punch_clock_ids) >= 4:
           intraday = (self.punch_clock_ids[2].punch_datetime) - (self.punch_clock_ids[1].punch_datetime)
           diference -= intraday
        if self.punch_clock_ids:
            horas = diference.seconds // 3600
            minutos = (diference.seconds % 3600) // 60
        self.daily_hours = str(horas) + ":" + str(minutos) if self.punch_clock_ids else "0:0"

    def add_punch(self):
        ctx = dict()
        ctx.update({

        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ponto Manual',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manual.point',
            'views': [[self.env.ref("punch_clock_integration.manual_point_form_view").id, 'form']],
            'context': ctx,
            'target': 'new'
        }
        #coloca o horário e ele preenche com o resto das informações

class ManualPoint(models.TransientModel):
    _name = 'manual.point'

    hour = fields.Datetime("Horário do Ponto")

    def confirm(self):
        pass
from odoo import models, fields
from datetime import timedelta


class PunchTime(models.TransientModel):
    _name = 'punch.time'

    manage_employee_time_id = fields.Many2one('manage.employee.time')
    employees_by_interval_id = fields.Many2one('employees.by.interval')
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    punch_date = fields.Many2many('punch.clock', string="Dia da Batida")
    punch_time = fields.Many2many('punch.clock.time', string="Batidas")
    worked_hour_related = fields.Char(related="punch_date.worked_hours", string="Trabalho")
    lunch_time_related = fields.Char(related="punch_date.lunch_time")
    attears_hour_related = fields.Char(related="punch_date.attears")
    extra_hour_hour_related = fields.Char(related="punch_date.extra_hour")
    extra_night_hours_related = fields.Char(related="punch_date.extra_night_hours")
    nighttime_supplement_related = fields.Char(related="punch_date.nighttime_supplement")
    employee_pis = fields.Char(string="PIS do Funcionário")
    justification = fields.Many2one('remoteness', string="Justificativa")
    week_day = fields.Char(string='Dia da semana')
    day = fields.Date(string='Dia')
    attention = fields.Selection(
        [('warning', 'Atenção'), ('success', 'Sucesso'), ('info', 'Info'), ('danger', 'Danger')])
    allow_move_creation = fields.Boolean()

    def return_extra_hours(self):
        ctx = dict()
        if self.justification and not self.justification.remuneration:
            day = self.env['workday'].search([('week_days_id', '=', self.env['week.days'].search(
                [('day', '=', self.day.strftime('%A').capitalize())]).id),('employee_id','=',self.employee_id)])
            departure_hours, departure_minutes = map(int, day.departure_hour.time.split(":"))
            departure_hour = timedelta(hours=departure_hours, minutes=departure_minutes)

            entrance_hours, entrance_minutes = map(int, day.entrance_hour.time.split(":"))
            entrance_hour = timedelta(hours=entrance_hours, minutes=entrance_minutes)
            if day.intraday > 0:
                to_work_hours = (departure_hour - entrance_hour) - timedelta(minutes=day.intraday)
            else:
                to_work_hours = departure_hour - entrance_hour
            if self.punch_time:
                worked_hours = self.punch_date.worked_hours.split(":")
                worked_hours = timedelta(hours=int(worked_hours[0]), minutes=int(worked_hours[1]))

                to_work_hours = to_work_hours - worked_hours

            ctx.update({
                'default_justification': str(to_work_hours),
            })

        ctx.update({
            'default_employee_id': self.manage_employee_time_id.employee_id.id,
            'default_date': self.day,
            'default_punch_clock_time_ids': self.punch_time.ids,
            'default_extra_hour_lunch': self.punch_date.extra_hour_lunch,
            'default_extra_hour': self.punch_date.extra_hour,
            'default_arrears_hour': self.punch_date.attears,
            'default_extra_night_hours': self.punch_date.extra_night_hours,
            'default_nighttime_supplement': self.punch_date.nighttime_supplement,
            'default_manage_employee_time_id': self.manage_employee_time_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Criar movimentações',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bank.register',
            'views': [[self.env.ref('punch_clock.bank_register_form_view').id, 'form']],
            'target': 'new',
            'context': ctx
        }

    def open_wizard(self):
        active_model = self.env.context.get("active_model")
        if active_model == 'manage.employee.time':
            view = "punch_clock.wizard_create_justification_form"
            ctx = self._context.copy()
            ctx.update({'parent_form': self.manage_employee_time_id.id,
                        'child_form': self.id,
                        'employee_id': self.manage_employee_time_id.employee_id.id,
                        'initial_date': self.day,
                        'final_date': self.day,
                        })
        else:
            view = "punch_clock.wizard_create_justification_form"
            ctx = self._context.copy()
            ctx.update({'parent_form': self.employees_by_interval_id.id,
                        'child_form': self.id,
                        'employee_id': self.employee_id.id,
                        'initial_date': self.day,
                        'final_date': self.day,
                        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Criar justificativas',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.justification',
            'views': [[self.env.ref(view).id, 'form']],
            'target': 'new',
            'context': ctx
        }

    def add_punch(self):
        active_model = self.env.context.get("active_model")
        if active_model == 'manage.employee.time':
            view = "punch_clock.manual_point_form_view"
            ctx = dict()
            ctx.update({
                'default_manage_employee_time_id': self.manage_employee_time_id.id,
                'default_date': self.day,
                'default_employee_id': self.employee_id.id,
            })
        else:
            view = "punch_clock.manual_point_form_view"
            ctx = dict()
            ctx.update({
                'default_employees_by_interval_id': self.employees_by_interval_id.id,
                'default_inicial_day_to_search': self.day,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Ponto Manual',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manual.point',
            'views': [[self.env.ref(view).id, 'form']],
            'context': ctx,
            'target': 'new',
        }

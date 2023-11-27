from odoo import models, fields, api
from datetime import timedelta


class PunchTime(models.TransientModel):
    _name = 'punch.time'

    manage_employee_time_id = fields.Many2one('manage.employee.time', string="Pesquisa por mês")
    employees_by_interval_id = fields.Many2one('employees.by.interval', string="Pesquisa por dia")
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    punch_date = fields.Many2one('punch.clock', string="Dia da Batida")
    punch_time = fields.Many2many('punch.clock.time', string="Batidas")
    worked_hour_related = fields.Char(related="punch_date.worked_hours", string="Trabalho")
    lunch_time_related = fields.Char(related="punch_date.lunch_time")
    attears_hour_related = fields.Char(related="punch_date.attears")
    extra_hour_hour_related = fields.Char(related="punch_date.extra_hour")
    employee_pis = fields.Char(string="PIS do Funcionário")
    justification = fields.Many2one('remoteness', string="Justificativa")
    week_day = fields.Char(string='Dia da semana')
    day = fields.Date(string='Dia')
    attention = fields.Selection([('warning', 'Atenção'),('success', 'Sucesso'),('info', 'Info'),('danger', 'Danger')],
                                 compute="_compute_attention")
    allow_move_creation = fields.Boolean()

    def _compute_attention(self):
        for rec in self:
            # Declaração de variáveis
            dsr_lack = []
            day = rec.day - timedelta(days=1)
            punch_ids = rec.punch_time.filtered(lambda punch: punch.status != 'disregarded')
            workday = self.env['workday'].search([('employee_id','=',rec.employee_id.id)]).mapped('week_days_id').mapped('day')
            intraday = self.env['workday'].search(
                [('employee_id', '=', rec.employee_id.id), ('week_days_id.day', '=', rec.week_day)]).intraday

            # Trativas para quando o dia iterado é o DSR do funcionário
            if rec.week_day == rec.employee_id.dsr_week_days_id.day:
                # Percorre até o dia do DSR anterior pra verificar se há uma falta
                while (day.strftime('%A').capitalize() != rec.employee_id.dsr_week_days_id.day):
                    justification = self.env['employee.remoteness'].search(
                        [('employee_remoteness_ids','in',rec.employee_id.id),('initial_date','<=',day),('final_date','>=',day)])

                    # Tratativas para caso o funcionário deva trabalhar nesse dia
                    if day.strftime('%A').capitalize() in workday:
                        # Caso o funcionário não tenha pontos
                        if not self.env['punch.clock'].search([('employee_id','=',rec.employee_id.id),('punch_date','=',day)]):
                            # Se não houver justificativa, atribui o dia da falta a uma lista
                            if not justification:
                                dsr_lack = day
                            else:# Se houver justificativa e ela não for remunerada, também vai para a lista
                                if not justification.remuneration:
                                    dsr_lack = day

                    day -= timedelta(days=1)
                # Caso essa lista tenha algum dia dentro dela, significa que há uma falta, e há perda do DSR
                if dsr_lack:
                    rec.attention = 'danger'
                else:
                    rec.attention = 'success'
            # Trativas para quando o dia iterado não é o DSR
            else:
                if rec.week_day not in workday:
                    rec.attention = 'info'
                else:
                    if len(punch_ids) < 4 and intraday > 0 or len(punch_ids) % 2 != 0 or len(punch_ids) % 2 == 0 and len(punch_ids) == 0:
                        rec.attention = 'warning'
                    else:
                        rec.attention = 'info'

    def return_extra_hours(self):
            ctx = dict()
            if self.justification and not self.justification.remuneration:
                day = self.env['workday'].search([('week_days_id', '=', self.env['week.days'].search(
                    [('day', '=', self.day.strftime('%A').capitalize())]).id),('employee_id','=',self.employee_id.id)])
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
                to_work_hours = str(to_work_hours).split(":")
                to_work_hours_in_seconds = (int(to_work_hours[0]) * 3600) + (int(to_work_hours[1]) * 60)
                formatted_hours = "{:02d}:{:02d}".format(to_work_hours_in_seconds // 3600,(to_work_hours_in_seconds % 3600) // 60)
                ctx.update({
                    'default_justification': formatted_hours,
                })
            ctx.update({
                'default_employee_id': self.employee_id.id,
                'default_date': self.day,
                'default_punch_clock_time_ids': self.punch_time.ids,
                'default_extra_hour_lunch': self.punch_date.extra_hour_lunch,
                'default_extra_hour': self.punch_date.extra_hour,
                'default_lunch_time': self.lunch_time_related,
                'default_extra_night_hours': self.punch_date.extra_night_hours,
                'default_interjourney': self.punch_date.interjourney,
                'default_nighttime_supplement': self.punch_date.nighttime_supplement,
                'default_manage_employee_time_id': self.manage_employee_time_id.id,
                'default_employees_by_interval_id': self.employees_by_interval_id.id,
                'default_arrears_hour': self.punch_date.attears,
                'default_punch_clock_id': self.punch_date.id,
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

    def open_wizard(self):# Função para criação de justificativa
        active_model = self.env.context.get("active_model")
        ctx = self._context.copy()
        if active_model == 'manage.employee.time':
            parent_form = self.manage_employee_time_id.id
            employee_id = self.manage_employee_time_id.employee_id.id
        else:
            parent_form = self.employees_by_interval_id.id
            employee_id = self.employee_id.id

        ctx.update({
            'parent_form': parent_form,
            'child_form': self.id,
            'employee_id': employee_id,
            'initial_date': self.day,
            'final_date': self.day,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Criar justificativas',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.justification',
            'views': [[self.env.ref("punch_clock.wizard_create_justification_form").id, 'form']],
            'target': 'new',
            'context': ctx
        }

    def add_punch(self):# Função para criação do ponto manual
        active_model = self.env.context.get("active_model")
        ctx = self._context.copy()
        if active_model == 'manage.employee.time':
            ctx.update({
                'default_manage_employee_time_id': self.manage_employee_time_id.id,
            })
        else:
            ctx.update({
                'default_employees_by_interval_id': self.employees_by_interval_id.id,
            })
        ctx.update({
                'default_date': self.day,
                'default_employee_id': self.employee_id.id,
                'punch_id': self.id
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ponto Manual',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manual.point',
            'views': [[self.env.ref("punch_clock.manual_point_form_view").id, 'form']],
            'context': ctx,
            'target': 'new',
        }
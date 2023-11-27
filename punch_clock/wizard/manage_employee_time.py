from odoo import models, fields, _, api
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.exceptions import UserError


class ManageEmployeeTime(models.TransientModel):
    _name = 'manage.employee.time'

    employee_id = fields.Many2one('hr.employee', string="Funcionário", required=True)
    punch_time_ids = fields.One2many('punch.time', 'manage_employee_time_id', string="Horarios")
    worked_hours_in_range = fields.Char(compute="compute_worked_hours_month")
    overtime_in_range = fields.Char(readonly=True)
    attears_hour_in_range = fields.Char(readonly=True)
    lack_dsr_and_lake = fields.Integer(readonly=True)
    month = fields.Selection([('01', 'Janeiro'),
                              ('02', 'Fevereiro'),
                              ('03', 'Março'),
                              ('04', 'Abril'),
                              ('05', 'Maio'),
                              ('06', 'Junho'),
                              ('07', 'Julho'),
                              ('08', 'Agosto'),
                              ('09', 'Setembro'),
                              ('10', 'Outubro'),
                              ('11', 'Novembro'),
                              ('12', 'Dezembro')
                              ], string="Mês", required=True)
    year = fields.Integer("Ano", default=int(date.today().year), required=True)

    def deltatime_to_hours_minutes(self,deltatime):
        total_minutes_work = deltatime.days * 24 * 60 + deltatime.seconds // 60
        hours_work = total_minutes_work // 60
        minutes_work = total_minutes_work % 60
        return hours_work, minutes_work

    def compute_worked_hours_month(self):
        worked_hours = timedelta()
        overtime = timedelta()
        arrears_hour = timedelta()
        lack_dsr_and_lack = 0

        # passa pelas batidas e soma os atributos acima de cada batida
        for rec in self.punch_time_ids:
            if rec.punch_date:
                worked_hours += rec.punch_date.compute_worked_hours()
                overtime += rec.punch_date.compute_extra_hour()
                splitted_attears = rec.punch_date.attears.split(":") if rec.punch_date.attears else [0,0]
                arrears_hour += timedelta(hours=int(splitted_attears[0]), minutes=int(splitted_attears[1]))
            elif rec.justification.id == self.env['remoteness'].search([('hypothesis', '=', 'Falta DSR')]).id:
                lack_dsr_and_lack += 1
            elif rec.justification.id == self.env['remoteness'].search(
                    [('hypothesis', '=', 'Faltas não justificadas')]).id:
                lack_dsr_and_lack += 1

        # separa hora e minuto de cada atributo
        format_work = self.deltatime_to_hours_minutes(worked_hours)
        format_overtime = self.deltatime_to_hours_minutes(overtime)
        format_arrears = self.deltatime_to_hours_minutes(arrears_hour)
        # formata os campos acima pra string
        self.worked_hours_in_range = "{:02d}:{:02d}".format(format_work[0], format_work[1])
        self.lack_dsr_and_lake = lack_dsr_and_lack
        self.overtime_in_range = "{:02d}:{:02d}".format(format_overtime[0], format_overtime[1])
        self.attears_hour_in_range = "{:02d}:{:02d}".format(format_arrears[0], format_arrears[1])

    def search_employee_punch(self):
        # Apaga a lista
        if self.punch_time_ids:
            self.punch_time_ids.unlink()

        # Validações
        if self.year > int(date.today().year):
            raise UserError(_("Impossível pesquisar ano maior que o ano atual"))
        if self.year < 0:
            raise UserError(_("Impossível pesquisar ano menor que 0"))

        # definindo o range de pesquisa
        today = datetime.today().date()
        inicial_day_to_search = today.replace(year=self.year, month=int(self.month), day=1)
        final_day_to_search = inicial_day_to_search + relativedelta(months=1)
        final_day_to_search -= timedelta(days=1)

        # declarando variaveis
        dsr_lack = []
        day = inicial_day_to_search

        # pesquisa justificativas do funcionario
        search_justifications = self.env['employee.remoteness'].sudo().search(
            [('employee_remoteness_ids', '=', self.employee_id.id), ('initial_date', '>=', inicial_day_to_search),
             ('final_date', '<=', final_day_to_search)])

        while final_day_to_search >= day:
            move = self.env['extract.virtual.hours'].search([
                ('employee_id', '=', self.employee_id.id), ('date', '=', day)])
            allow_move_creation = True if not move else False

            # Valida se há justificativa para o dia iterado
            justifications = search_justifications.filtered(lambda x: day >= x.initial_date and day <= x.final_date)
            punch_ids = self.env['punch.clock'].search(
                [('punch_date', '=', day), ('employee_pis', '=', self.employee_id.employee_pis)])
            punch_time = self.env['punch.clock.time'].search([('day_id', 'in', punch_ids.ids)])

            vals = {
                'manage_employee_time_id': self.id,
                'employee_id': self.employee_id.id,
                'punch_date': punch_ids.id,
                'punch_time': punch_time.ids if punch_ids else False,
                'justification': justifications[0].reason.id if justifications else False,
                'week_day': day.strftime('%A').capitalize(),
                'day': day,
                'allow_move_creation': allow_move_creation,
            }
            self.env['punch.time'].create(vals)

            day += timedelta(days=1)

        # se houver falta de um dsr que não esta no range de pesquisa adiciona falta no proximo dsr
        for rec in dsr_lack:
            move = self.env['extract.virtual.hours'].search([
                ('employee_id', '=', self.employee_id.id), ('date', '=', rec)])
            allow_move_creation = True if not move else False

            vals = {
                'manage_employee_time_id': self.id,
                'employee_id': self.employee_id.id,
                'justification': self.env['remoteness'].search([('hypothesis', '=', 'Falta DSR')]).id,
                'week_day': rec.strftime('%A').capitalize(),
                'day': rec,
                'allow_move_creation':allow_move_creation,
            }
            self.env['punch.time'].create(vals)

        ctx = dict()
        ctx.update({
            'default_month': self.month,
            'default_year': self.year,
            'default_employee_id': self.employee_id.id,
            'default_punch_time_ids': self.punch_time_ids.ids,
            'default_worked_hours_in_range': self.worked_hours_in_range,
            'default_attears_hour_in_range': self.attears_hour_in_range,
            'default_overtime_in_range': self.overtime_in_range,
            'default_lack_dsr_and_lake': self.lack_dsr_and_lake,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pesquisa de ponto',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manage.employee.time',
            'views': [[self.env.ref("punch_clock.manage_employee_time_form").id, 'form']],
            'context': ctx,
            'target': 'new'
        }
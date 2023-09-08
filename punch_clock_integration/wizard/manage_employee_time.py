from odoo import models, fields, _
import datetime
from odoo.exceptions import Warning, UserError
from dateutil.relativedelta import relativedelta


class ManageEmployeeTime(models.TransientModel):
    _name = 'manage.employee.time'

    filter = fields.Selection([('range','Intervalo de Dias'),
                               ('day','Dia'),
                               ('month','Consulta Mensal'),
                               ('week', 'Intervalo de semana'),
                               # ('week_range', 'Consulta semanal')
                                ], string="Opções de Pesquisa")
    punch_time_ids = fields.One2many('punch.time', 'manage_employee_time_id', string="Horarios")
    day_to_search = fields.Date(string="Dia a pesquisar")
    last_day = fields.Date(string="Dia final")
    month = fields.Selection([('01','Janeiro'),
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
                              ],string="Mês")
    year = fields.Integer("Ano")
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    monthly_hours = fields.Char(readonly=True, string="Horas Trabalhadas")
    expected_hours = fields.Char(readonly=True)
    attrs_bool = fields.Boolean()
    ideal_hours = fields.Integer("Horas Ideais")
    extra_hour = fields.Char("Horas Excedentes", readonly=True)
    debtor_hour = fields.Char("Horas Devedoras", readonly=True)

    def search_employee_punch(self):
        if self.punch_time_ids:
            self.punch_time_ids.unlink()
        domain = []
        if self.filter == 'range':
            domain.append(('punch_datetime', '>=', self.day_to_search))
            domain.append(('punch_datetime', '<=', self.last_day))
        elif self.filter == 'day':
            domain.append(('punch_datetime', '>=', self.day_to_search))
            domain.append(('punch_datetime', '<', self.day_to_search + datetime.timedelta(days=1)))
        elif self.filter == 'month':
            domain.append(('employee_pis', '=', self.employee_id.employee_pis))
            data_inicial = datetime.datetime(self.year, int(self.month), 1)
            data_final = data_inicial + relativedelta(months=1, days=-1, hours=23, minutes=59)
            domain.append(('punch_datetime', '>=', data_inicial))
            domain.append(('punch_datetime', '<=', data_final))

        punch_ids = self.env['punch.clock'].search(domain)
        if not punch_ids:
            raise Warning(_("Não há resultados para essa pesquisa."))
        else:
            ctx = dict()
            if self.filter == 'range':
                for pis in punch_ids.mapped('employee_pis'):# talvez tirar as duplicatas (?)
                    # ta fazendo o for um monte de vez aqui e faz ali embaixo tambem ai vem muitos registros
                    days_range = self.last_day - self.day_to_search
                    days_range = days_range.days + 1
                    i = self.day_to_search
                    for day in range(days_range):
                        employee_punch_ids = punch_ids.filtered(lambda lm: lm.employee_pis == pis and lm.punch_datetime.date() == i)
                        vals = {
                            'manage_employee_time_id': self.id,
                            'employee_id': self.env['hr.employee'].search([('employee_pis','=',pis)]).id,
                            'punch_clock_ids': employee_punch_ids.ids,
                            'date': i,
                            'employee_pis': pis,
                        }
                        i += datetime.timedelta(days=1)
                        self.env['punch.time'].create(vals)
            elif self.filter == 'day':
                for pis in punch_ids.mapped('employee_pis'):
                    employee_punch_ids = punch_ids.filtered(lambda lm: lm.employee_pis == pis)
                    vals = {
                        'manage_employee_time_id': self.id,
                        'employee_id': self.env['hr.employee'].search([('employee_pis','=',pis)]).id,
                        'punch_clock_ids': employee_punch_ids.ids,
                        'employee_pis': pis,
                    }
                    self.env['punch.time'].create(vals)
            elif self.filter == 'month':
                #calcular horas devedoras!
                #testar colocar falta abonada e nao justificada e calcular certinho
                #interessante mostrar cada um por dia

                #cálculo do intervalo de dias e contador de dia
                days_range = data_final - data_inicial
                days_range = days_range.days + 1
                i = data_inicial.date()
                seconds_diference = 0

                #Lista que contém os dias que o funcionário trabalha
                work_days = self.employee_id.workday_ids.week_days_id.mapped('day')

                for index,day in enumerate(range(days_range)):
                    week_day = i.strftime('%A').capitalize()
                    employee_punch_ids = punch_ids.filtered(lambda lm: lm.punch_datetime.date() == i)
                    first = employee_punch_ids[0].punch_datetime if employee_punch_ids else 0
                    last = employee_punch_ids[-1].punch_datetime if employee_punch_ids else 0
                    diference = (last)-(first)
                    seconds_diference += diference.seconds if employee_punch_ids else 0
                    if len(employee_punch_ids.ids) >= 4:
                        intraday = employee_punch_ids[2].punch_datetime - employee_punch_ids[1].punch_datetime
                        seconds_diference -= intraday.seconds
                    vals = {
                        'manage_employee_time_id': self.id,
                        'employee_id': self.employee_id.id,
                        'punch_clock_ids': employee_punch_ids.ids,
                        'date': i,
                        'week_day': week_day,
                        'should_work': True if week_day in work_days else False,
                    }
                    if week_day in work_days:
                        if work_days == "Sábado":
                            self.ideal_hours += 4
                        else:
                            self.ideal_hours += 8
                    i += datetime.timedelta(days=1)
                    self.env['punch.time'].create(vals)
                    if index == days_range - 1:
                        horas = seconds_diference // 3600
                        minutos = (seconds_diference % 3600) // 60
                        self.monthly_hours = str(horas) + ":" + str(minutos)

                worked_hour, worked_minute = map(int, self.monthly_hours.split(':'))
                worked_seconds = (worked_hour * 3600 + worked_minute * 60)
                debtor_hours = (self.ideal_hours * 3600) - worked_seconds
                extra_hours = worked_seconds - (self.ideal_hours * 3600)
                self.debtor_hour = str(debtor_hours // 3600) + ":" + str((debtor_hours % 3600) // 60) if (self.ideal_hours*3600) > worked_seconds else 0
                self.extra_hour = str(extra_hours // 3600) + ":" + str((extra_hours % 3600) // 60) if (self.ideal_hours*3600) < worked_seconds else 0
                ctx.update({
                    'default_attrs_bool': True,
                    'default_monthly_hours': self.monthly_hours,
                    'default_ideal_hours': self.ideal_hours,
                    'default_debtor_hour': self.debtor_hour,
                    'default_extra_hour': self.extra_hour,
                })
            else:
                first_work_day = self.day_to_search.strftime('%A').upper()
                last_work_day = self.last_day.strftime('%A').upper()
                # fazer um campo que mostra se o funcionario trabalhou mais ou menos das horas necessárias do mes
                # pra cada dia, se o funcionário for trabalhar nesse dia, adicionar horas q ele deve trabalhar nesse dia
                # calcular adicional noturno se for permitido no sindicato do funcionario
                # calcular he se nao tiver devedora, se nao, só subtrai do saldo de horas
                # relevar atrasos e horas extras se forem dentro do range de 10 minutos
                # calcular falta por semana, se ele vai perder o dsr

                # FAZER COMPARAÇÃO COM O PRIMEIRO E O ULTIMO DIA DE TRABALHO DO FUNCIONARIO
                # if first_work_day != self.env['week.days'].browse(self.employee_id.week_days_ids[0].id).day.upper() \
                #         or last_work_day != self.env['week.days'].browse(self.employee_id.week_days_ids[-1].id).day.upper():
                #     raise UserError(_("Selecione uma segunda-feira e uma sexta-feira respectivamente."))
                days_range = self.last_day - self.day_to_search
                days_range = days_range.days + 1
                i = self.day_to_search
                seconds_diference = 0
                for index, day in enumerate(range(days_range)): #Pontos referentes ao funcionario e a data seguem abaixo
                    week_day = i.strftime('%A').capitalize()
                    employee_punch_ids = punch_ids.filtered(
                        lambda lm: lm.employee_pis == self.employee_id.employee_pis and lm.punch_datetime.date() == i)

                    #Cálculo de horas trabalhadas
                    first = employee_punch_ids[0].punch_datetime if employee_punch_ids else 0
                    last = employee_punch_ids[-1].punch_datetime if employee_punch_ids else 0
                    diference = (last) - (first)
                    seconds_diference += diference.seconds if employee_punch_ids else 0
                    if len(employee_punch_ids.ids) >= 4:
                        intraday = employee_punch_ids[2].punch_datetime - employee_punch_ids[1].punch_datetime
                        seconds_diference -= intraday.seconds

                    vals = {
                        'manage_employee_time_id': self.id,
                        'employee_id': self.employee_id.id,
                        'punch_clock_ids': employee_punch_ids.ids,
                        'date': i,
                        'employee_pis': self.employee_id.employee_pis,
                        'week_day': week_day,
                    }
                    i += datetime.timedelta(days=1)
                    self.env['punch.time'].create(vals)
                    #horas devedoras também
                    #arranjar maneira de mostrar as horas devedoras
                    if index == days_range - 1:
                        subtraction = 44 if len(self.employee_id.workday_ids) == 6 else 40
                        horas = seconds_diference // 3600
                        he = (seconds_diference // 3600) - subtraction
                        # dh =
                        minutos = (seconds_diference % 3600) // 60
                        self.monthly_hours = str(horas) + ":" + str(minutos)

                        self.extra_hour = str(he) + ":" + str(minutos) if horas >= subtraction else str(0)
                ctx.update({
                    'default_attrs_bool': True,
                    'default_monthly_hours': self.monthly_hours,
                    'default_extra_hour': self.extra_hour,
                })
            ctx.update({
                'default_day_to_search': self.day_to_search,
                'default_employee_id': self.employee_id.id,
                'default_last_day': self.last_day,
                'default_punch_time_ids': self.punch_time_ids.ids,
                'default_filter': self.filter,
                'default_month': self.month,
                'default_year': self.year,
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pesquisa de ponto',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'manage.employee.time',
                'views': [[self.env.ref("punch_clock_integration.manage_employee_time_form").id, 'form']],
                'context': ctx,
                'target': 'new'
            }

    def search_employee_wrong_time(self):
        if self.punch_time_ids:
            self.punch_time_ids.unlink()
        domain = []
        if self.filter == 'week':
            domain.append(('punch_datetime', '>=', self.day_to_search))
            domain.append(('punch_datetime', '<=', self.last_day))
            domain.append(('employee_id', '=', self.employee_id.id))

        punch_ids = self.env['punch.clock'].search(domain)
        if not punch_ids:
            raise Warning(_("Não há resultados para essa pesquisa."))
        else:
            if self.filter == 'week':
                days_range = self.last_day - self.day_to_search
                days_range = days_range.days + 1
                i = self.day_to_search
                week_day = i.strftime('%A').upper()
                for day in range(days_range):
                    employee_punch_ids = punch_ids.filtered(
                        lambda lm: lm.punch_datetime.date() == i)
                    if len(employee_punch_ids) / 4 != 0 and len(employee_punch_ids) != 0:
                        a = self.employee_id.workday_ids.filtered(lambda lm:lm.week_days_id.day.upper() == week_day).mapped('hour_ids')[0].time
                        b = self.employee_id.workday_ids.filtered(lambda lm:lm.week_days_id.day.upper() == week_day).mapped('hour_ids')[-1].time
                        fh = (datetime.datetime.strptime(a, "%H:%M")  - datetime.timedelta(hours=3)).time()
                        lh = (datetime.datetime.strptime(b, "%H:%M") - datetime.timedelta(hours=3)).time()
                        entrada_negativa = (employee_punch_ids[0].punch_datetime - datetime.timedelta(minutes=10)).time()
                        entrada_positiva = (employee_punch_ids[0].punch_datetime + datetime.timedelta(minutes=10)).time()
                        saida_negativa = (employee_punch_ids[3].punch_datetime + datetime.timedelta(minutes=10)).time() if len(employee_punch_ids) == 4 else 0
                        saida_positiva = (employee_punch_ids[3].punch_datetime - datetime.timedelta(minutes=10)).time() if len(employee_punch_ids) == 4 else 0
                        if entrada_positiva < fh or entrada_negativa > fh or saida_positiva > lh or saida_negativa < lh:
                            vals = {
                                'manage_employee_time_id': self.id,
                                'employee_id': self.employee_id.id,
                                'punch_clock_ids': employee_punch_ids.ids,
                                'date': i,
                                'employee_pis': self.employee_id.employee_pis,
                            }
                            self.env['punch.time'].create(vals)
                    i += datetime.timedelta(days=1)
                ctx = dict()
                ctx.update({
                    'default_day_to_search': self.day_to_search,
                    'default_last_day': self.last_day,
                    'default_employee_id': self.employee_id.id,
                    'default_punch_time_ids': self.punch_time_ids.ids,
                    'default_filter': self.filter,
                })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pesquisa de ponto',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'manage.employee.time',
                'views': [[self.env.ref("punch_clock_integration.manage_employee_time_form").id, 'form']],
                'context': ctx,
                'target': 'new'
            }
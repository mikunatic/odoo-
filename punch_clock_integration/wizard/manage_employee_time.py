from odoo import models, fields, _, api
import datetime
from odoo.exceptions import Warning, UserError
from dateutil.relativedelta import relativedelta


class ManageEmployeeTime(models.TransientModel):
    _name = 'manage.employee.time'

    filter = fields.Selection([('range','Intervalo de Dias'),
                               ('day','Dia'),
                               ('month','Consulta Mensal'),
                               ('week', 'Divergências de horários de funcionário'),
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
    monthly_hours = fields.Char(readonly=True, string="Horas Trabalhadas", compute="_compute_monthly_hours")
    expected_hours = fields.Char(readonly=True)
    attrs_bool = fields.Boolean()
    ideal_hours = fields.Char("Horas Ideais", compute="_compute_ideal_hours")
    extra_hour = fields.Char("Horas Excedentes", readonly=True)
    debtor_hour = fields.Char("Horas Devedoras", readonly=True)

    def _compute_ideal_hours(self):
        ideal_seconds = 0
        for day in self.punch_time_ids:
            allowed_intraday = self.env['workday'].search(
                [('week_days_id.day', '=', day.week_day), ('employee_id', '=', self.employee_id.id)]).intraday

            # Cálculo em segundos das horas ideais do funcionário
            if day.should_work:
                if allowed_intraday:
                    # Cálculo em segundos do tempo de intrajornada do funcionário
                    intraday_id = self.env['hr.employee'].browse(self.employee_id.id).mapped('intraday')
                    multiplier = 1 if intraday_id.hour_minute_selection == 'minute' else 60
                    intraday_seconds = (intraday_id.value * multiplier) * 60
                    workday_seconds = self.calculate_seconds(day.week_day)

                    ideal_seconds += (workday_seconds) - intraday_seconds
                else:
                    ideal_seconds += self.calculate_seconds(day.week_day)

        #Atribuição de valores para os campos de horas trabalhadas e as horas ideais do funcionário
        self.ideal_hours = str(ideal_seconds // 3600) + ":" + str((ideal_seconds % 3600) // 60)

    def _compute_monthly_hours(self):
        seconds_diference = 0
        for day in self.punch_time_ids:
            allowed_intraday = self.env['workday'].search(
                [('week_days_id.day', '=', day.week_day), ('employee_id', '=', self.employee_id.id)]).intraday

            # Cálculo que armazena na variável seconds_diference quantas horas, em segundos, que o funcionário trabalhou
            first = day.punch_clock_ids[0].punch_datetime if day.punch_clock_ids else 0
            last = day.punch_clock_ids[-1].punch_datetime if day.punch_clock_ids else 0
            diference = (last) - (first)
            seconds_diference += diference.seconds if day.punch_clock_ids else 0
            if len(day.punch_clock_ids.ids) >= 4:
                intraday = day.punch_clock_ids[2].punch_datetime - day.punch_clock_ids[1].punch_datetime
                seconds_diference -= intraday.seconds

            # Se o afastamento for remunerado, o funcionário recebe de volta as horas
            if day.remoteness_id and day.remoteness_id.remuneration:# Adiciona as horas trabalhadas caso a falta seja remunerada
                if allowed_intraday:
                    compensed_seconds = self.calculate_seconds(day.week_day)
                    intraday_id = self.env['hr.employee'].browse(self.employee_id.id).mapped('intraday')
                    multiplier = 1 if intraday_id.hour_minute_selection == 'minute' else 60
                    intraday_seconds = (intraday_id.value * multiplier) * 60
                    seconds_diference += (compensed_seconds) - intraday_seconds
                else:
                    seconds_diference += self.calculate_seconds(day.week_day)

        # Cálculo de horas trabalhadas
        horas = seconds_diference // 3600
        minutos = (seconds_diference % 3600) // 60
        self.monthly_hours = str(horas) + ":" + str(minutos)

        # Cálculo de horas extras ou devedoras
        ideal_hours, ideal_minutes = map(int,self.ideal_hours.split(':'))
        ideal_seconds = (ideal_hours * 3600) + (ideal_minutes * 60)
        debtor_hours = ideal_seconds - seconds_diference
        extra_hours = seconds_diference - ideal_seconds
        self.debtor_hour = str(debtor_hours // 3600) + ":" + str((debtor_hours % 3600) // 60) if ideal_seconds > seconds_diference else 0
        self.extra_hour = str(extra_hours // 3600) + ":" + str((extra_hours % 3600) // 60) if ideal_seconds < seconds_diference else 0

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
                #Cálculo do intervalo de dias e contador de dia
                days_range = data_final - data_inicial
                days_range = days_range.days + 1
                i = data_inicial.date()

                #Lista que contém os dias que o funcionário trabalha
                work_days = self.employee_id.workday_ids.week_days_id.mapped('day')

                for day in range(days_range):
                    week_day = i.strftime('%A').capitalize()# Variável que armazena o dia da semana
                    allowed_intraday = self.env['workday'].search(
                        [('week_days_id.day', '=', week_day), ('employee_id', '=', self.employee_id.id)]).intraday
                    remoteness_id = self.env['remoteness']
                    employee_punch_ids = punch_ids.filtered(lambda lm: lm.punch_datetime.date() == i)# Pontos do dia iterado do funcionário
                    should_work = True if week_day in work_days else False

                    #Validação da justificativa adequada
                    #erro no search
                    justification_id = self.env['justification'].search([
                        ('first_day','<=',i),('last_day','>=',i),('employee_id','=',self.employee_id.id)])
                    if not employee_punch_ids and should_work and not justification_id:
                        remoteness_id = self.env['remoteness'].browse(26)
                    if justification_id:
                        remoteness_id = justification_id.remoteness_id

                    #Verificação se os pontos estão diferentes do esperado
                    if should_work and allowed_intraday and not remoteness_id:
                        if len(employee_punch_ids) != 4:
                            divergent_punchs = True
                        else:
                            divergent_punchs = False
                    elif should_work and not allowed_intraday and not remoteness_id:
                        if len(employee_punch_ids) != 2:
                            divergent_punchs = True
                        else:
                            divergent_punchs = False
                    else:
                        divergent_punchs = False

                    #Criação da tabela da pesquisa
                    vals = {
                        'manage_employee_time_id': self.id,
                        'employee_id': self.employee_id.id,
                        'punch_clock_ids': employee_punch_ids.ids,
                        'date': i,
                        'week_day': week_day,
                        'should_work': should_work,
                        'remoteness_id': remoteness_id.id if remoteness_id else False,
                        'justification_id': justification_id.id,
                        'divergent_punchs': divergent_punchs,
                    }
                    i += datetime.timedelta(days=1)
                    self.env['punch.time'].create(vals)

                ctx.update({
                    'default_attrs_bool': True,
                    'default_monthly_hours': self.monthly_hours,
                    'default_ideal_hours': self.ideal_hours,
                    'default_debtor_hour': self.debtor_hour,
                    'default_extra_hour': self.extra_hour,
                })
                # calcular adicional noturno se for permitido no sindicato do funcionario
                # relevar atrasos e horas extras se forem dentro do range de 10 minutos
                # calcular falta por semana, se ele vai perder o dsr

            elif self.filter == 'week':
                if self.filter == 'week':
                    days_range = self.last_day - self.day_to_search
                    days_range = days_range.days + 1
                    i = self.day_to_search
                    justification = self.env['justification'].search(
                        ['&', '|', ('employee_id', '=', self.employee_id.id), ('first_day', '>=', self.day_to_search),
                         ('last_day', '<=', self.last_day)])
                    for day in range(days_range):
                        week_day = i.strftime('%A').capitalize()
                        employee_punch_ids = punch_ids.filtered(
                            lambda lm: lm.punch_datetime.date() == i)
                        justification_id = justification.filtered(
                            lambda lm: lm.first_day <= i <= lm.last_day) or False
                        if len(employee_punch_ids) / 4 != 0 and len(employee_punch_ids) != 0:
                            convert_entrance_hour = self.employee_id.workday_ids.filtered(
                                lambda lm: lm.week_days_id.day.capitalize() == week_day).mapped('hour_ids')[0].time
                            convert_exit_hour = self.employee_id.workday_ids.filtered(
                                lambda lm: lm.week_days_id.day.capitalize() == week_day).mapped('hour_ids')[-1].time
                            fh = (datetime.datetime.strptime(convert_entrance_hour, "%H:%M") + datetime.timedelta(
                                hours=0)).time()
                            lh = (datetime.datetime.strptime(convert_exit_hour, "%H:%M") + datetime.timedelta(
                                hours=0)).time()
                            zero_time = datetime.datetime(1, 1, 1, 0, 0, 0).time()
                            entrada_negativa = (
                                    employee_punch_ids[0].punch_datetime - datetime.timedelta(minutes=10)).time()
                            entrada_positiva = (
                                    employee_punch_ids[0].punch_datetime + datetime.timedelta(minutes=10)).time()
                            saida_negativa = (employee_punch_ids[3].punch_datetime + datetime.timedelta(
                                minutes=10)).time() if len(employee_punch_ids) == 4 else zero_time
                            saida_positiva = (employee_punch_ids[3].punch_datetime - datetime.timedelta(
                                minutes=10)).time() if len(employee_punch_ids) == 4 else zero_time
                            intraday = self.employee_id.workday_ids.filtered(lambda lm: lm.intraday == False)
                            if entrada_positiva < fh or entrada_negativa > fh or saida_positiva > lh or saida_negativa < lh or len(
                                    employee_punch_ids) != 4:
                                not_work_day = intraday.week_days_id
                                not_work_day = not_work_day.mapped('day')
                                if week_day in not_work_day:
                                    i += datetime.timedelta(days=1)
                                    continue
                                else:
                                    vals = {
                                        'manage_employee_time_id': self.id,
                                        'employee_id': self.employee_id.id,
                                        'punch_clock_ids': employee_punch_ids.ids,
                                        'date': i,
                                        'week_day': week_day,
                                        'employee_pis': self.employee_id.employee_pis,
                                        'justification_id': justification_id.remoteness_id.hypothesis if justification_id else False,

                                    }
                                    self.env['punch.time'].create(vals)
                        elif justification_id:
                            vals = {
                                'manage_employee_time_id': self.id,
                                'employee_id': self.employee_id.id,
                                'punch_clock_ids': False,
                                'date': i,
                                'week_day': week_day,
                                'employee_pis': self.employee_id.employee_pis,
                                'justification_id': justification_id.remoteness_id.hypothesis,
                            }
                            self.env['punch.time'].create(vals)
                        i += datetime.timedelta(days=1)
            # ctx = dict()
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

    def calculate_seconds(self, week_day):
        # Armazena a hora de entrada e saída do dia do funcionário
        hour_ids = self.env['workday'].search([
            ('week_days_id.day', '=', week_day),('employee_id','=',self.employee_id.id)]).mapped('hour_ids')

        # Transforma as horas em segundos para facilidade no cálculo
        first_hour, first_minute = map(int, hour_ids[0].time.split(':'))
        first_seconds = first_hour * 3600 + first_minute * 60
        last_hour, last_minute = map(int, hour_ids[-1].time.split(':'))
        last_seconds = last_hour * 3600 + last_minute * 60
        result = last_seconds - first_seconds
        return result
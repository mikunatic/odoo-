from odoo import models, fields, _, api
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import date


class ManageEmployeeTime(models.TransientModel):
    _name = 'manage.employee.time'

    inicial_day_to_search = fields.Date(string="Dia inicial")
    final_day_to_search = fields.Date(string="Dia final")
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    punch_time_ids = fields.One2many('punch.time', 'manage_employee_time_id', string="Horarios")
    worked_hours_in_range = fields.Char(compute="compute_worked_hours_mounth")
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
                              ], string="Mês")
    year = fields.Integer("Ano", default=int(date.today().year))

    # @api.onchange('punch_time_ids')
    def create_virtual_bank_line(self):
        #fazer create de linha do virtual bank de acordo com as informações dessa pesquisa
        #verificar o tipo de horas e colocar de acordo
        #fazer for nas linhas da pesquisa para facilitar na criação das linhas do virtual bank
        # ESTÁ FALTANDO A MOVIMENTAÇÃO PARA QUANDO HÁ FALTA, E FALTA DSR, SÓ HÁ ATRASO NO DÉBITO
        if self.punch_time_ids:
            for line in self.punch_time_ids:
                # if line.extra_hour_hour_related:
                    punch_clock_id = line.punch_date.ids
                    #verificar se já tem o registro com esse dia criado
                    move = self.env['virtual.bank'].search([('employee_id','=',self.employee_id.id),
                                                            ('date','=',line.day)])
                    if not move:
                        #Hora excedente
                        if punch_clock_id.extra_hour != '00:00':
                            hours, minutes = map(int, punch_clock_id.extra_hour.split(':'))
                            vals_list = {
                                'date': punch_clock_id.punch_date,
                                'hours': punch_clock_id.extra_hour,
                                'employee_id': self.employee_id.id,
                                'movement_type': 'credit.virtual.bank, {}'.format(self.env['credit.virtual.bank'].search(
                                    [('name', '=like', 'HE 50%')]).id),
                                'seconds': (int(hours) * 3600) + (int(minutes) * 60),
                            }
                            self.env['virtual.bank'].create(vals_list)
                        #Hora extra de almoço
                        if punch_clock_id.extra_hour_lunch != '00:00':
                            hours, minutes = map(int, punch_clock_id.extra_hour_lunch.split(':'))
                            vals_list = {
                                'date': punch_clock_id.punch_date,
                                'hours': punch_clock_id.extra_hour_lunch,
                                'employee_id': self.employee_id.id,
                                'movement_type': 'credit.virtual.bank, {}'.format(self.env['credit.virtual.bank'].search(
                                    [('name', '=like', 'HE 50%')]).id),
                                'seconds': (int(hours) * 3600) + (int(minutes) * 60),
                            }
                            self.env['virtual.bank'].create(vals_list)
                        #Atraso
                        if punch_clock_id.attears != '00:00':
                            hours, minutes = map(int, punch_clock_id.attears.split(':'))
                            vals_list = {
                                'date': punch_clock_id.punch_date,
                                'hours': punch_clock_id.attears,
                                'employee_id': self.employee_id.id,
                                'movement_type': 'debit.virtual.bank, {}'.format(self.env['debit.virtual.bank'].search(
                                    [('name', '=like', 'Faltas horas/atraso')]).id),
                                'seconds': (int(hours) * 3600) + (int(minutes) * 60),
                            }
                            self.env['virtual.bank'].create(vals_list)
                    else:
                        pass

                # fazer criação caso tenha bonus aqui
                # verificar o tipo de hora, se é noturna, qual he

    def deltatime_to_hours_minutes(self, deltatime):#objeto de tempo em uma lista onde são retornadas horas e minutos separadamente
        total_minutes_work = deltatime.days * 24 * 60 + deltatime.seconds // 60
        hours_work = total_minutes_work // 60
        minutes_work = total_minutes_work % 60
        return hours_work, minutes_work

    def compute_worked_hours_mounth(self):#
        worked_hours = timedelta()
        overtime = timedelta()
        arrears_hour = timedelta()
        lack_dsr_and_lack = 0

        #passa pelas batidas e soma os atributos acima de cada batida
        for rec in self.punch_time_ids:
            if rec.punch_date:
                worked_hours += rec.punch_date.compute_virtual_time()
                overtime += rec.punch_date.compute_extra_hour()
                arrears_hour += rec.punch_date.compute_attears()
            elif rec.justification.id == self.env['remoteness'].search([('hypothesis','=','Falta DSR')]).id:
                lack_dsr_and_lack += 1
            elif rec.justification.id == self.env['remoteness'].search([('hypothesis','=','Faltas não justificadas')]).id:
                lack_dsr_and_lack += 1

        # separa hora e minuto de cada atributo
        format_work = self.deltatime_to_hours_minutes(worked_hours)
        format_overtime = self.deltatime_to_hours_minutes(overtime)
        format_arrears = self.deltatime_to_hours_minutes(arrears_hour)
        # formata os campos acima pra string
        self.worked_hours_in_range = "{:02d}:{:02d}".format(format_work[0],format_work[1])
        self.lack_dsr_and_lake = lack_dsr_and_lack
        self.overtime_in_range = "{:02d}:{:02d}".format(format_overtime[0],format_overtime[1])
        self.attears_hour_in_range = "{:02d}:{:02d}".format(format_arrears[0],format_arrears[1])

    def search_employee_punch(self):
        #apagar todas a lista de batidas pra evitar problemas
        if self.punch_time_ids:
            self.punch_time_ids.unlink()

        # definindo o range de pesquisa
        today = datetime.today().date()
        inicial_day_to_search = today.replace(year=self.year, month=int(self.month),day=1)
        final_day_to_search = inicial_day_to_search + relativedelta(months=1)
        final_day_to_search -= timedelta(days=1)

        #pesquisa feriados
        holiday = self.env['holiday'].search([('inicial_date', '>=', inicial_day_to_search),
                                              ('final_date', '<=', final_day_to_search)])

        # declarando variaveis
        dsr_lack = []
        records = []
        day = inicial_day_to_search

        #pesquisa todos os pontos do funcionario
        punch_clock_ids = self.env['punch.clock'].search([('punch_date','>=',inicial_day_to_search),('punch_date','<=',final_day_to_search),('employee_pis','=',self.employee_id.employee_pis)])
        punch_ids_date = punch_clock_ids.mapped('punch_date')

        #pesquisa justificativas do funcionario
        search_justifications = self.env['employee.remoteness'].sudo().search(
            [('employee_id', '=',self.employee_id.id), ('initial_date', '>=', inicial_day_to_search),
             ('final_date', '<=', final_day_to_search)])

        #!!!!!!!IMPORTANTE!!!!!!!

        #fazer dica das vals que mila falou

        while final_day_to_search >= day:
            # valida se a justificativa para o dia da iteração do while
            justifications = search_justifications.filtered(lambda x: day >= x.initial_date and day <= x.final_date)
            punch_ids = self.env['punch.clock'].search(
                [('punch_date', '=', day), ('employee_pis', '=', self.employee_id.employee_pis)])
            punch_time = self.env['punch.clock.time'].search([('day_id', 'in', punch_ids.ids)])

            # valida se a feriados para o dia da iteração do while
            is_holiday = holiday.filtered(lambda x: day <= x.final_date and day >= x.inicial_date)

            #verifica se é dia de trabalho
            day_object = self.env['week.days'].search(
                [('day', '=', day.strftime('%A').capitalize())]).id
            workday = self.employee_id.workday_id.week_days_id.mapped('id')

            if day in dsr_lack:#verifica se tem alguma falta dsr
                dsr_lack.remove(day)
                vals = {
                    'manage_employee_time_id': self.id,
                    'employee_id': self.employee_id.id,
                    'punch_date': punch_ids.ids,
                    'punch_time': punch_time.ids if punch_ids else False,
                    'justification': self.env['remoteness'].search([('hypothesis','=','Falta DSR')]).id,
                    'attention': 'danger',
                    'week_day': day.strftime('%A').capitalize(),
                    'day': day
                }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)

            elif is_holiday: #verifica se existe feriado pro funcionario
                vals = {
                    'manage_employee_time_id': self.id,
                    'punch_date': punch_ids.ids,
                    'punch_time': punch_time.ids,
                    'employee_id': self.employee_id.id,
                    'justification': self.env['remoteness'].search([('hypothesis','=','Feriados')]).id,
                    'attention': 'warning' if len(punch_time) != 4 else 'success',
                    'week_day': day.strftime('%A').capitalize(),
                    'day': day
                }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)

            elif day_object == self.employee_id.dsr_week_days_id.id:#registra dsr do funcionario
                vals = {
                    'manage_employee_time_id': self.id,
                    'employee_id': self.employee_id.id,
                    'punch_date': punch_ids.ids,
                    'punch_time': punch_time.ids if punch_ids else False,
                    'justification': self.env['remoteness'].search([('hypothesis','=','DSR')]).id,
                    'attention': 'success',
                    'week_day': day.strftime('%A').capitalize(),
                    'day': day
                }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)

            elif day_object not in workday and day_object != self.employee_id.dsr_week_days_id.id:
                #dia compensado ou seja dia que não esta na lista de trabalho(mudar depois colocar dia compensado na lista porem com boolean para diferenciar)
                vals = {
                    'manage_employee_time_id': self.id,
                    'employee_id': self.employee_id.id,
                    'punch_date': punch_ids.ids,
                    'punch_time': punch_time.ids if punch_ids else False,
                    'justification': self.env['remoteness'].sudo().search([('hypothesis','=','Dia compensado')]).id,
                    'attention': 'success',
                    'week_day': day.strftime('%A').capitalize(),
                    'day': day
                }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)

            elif day in punch_ids_date:#se os pontos existirem eles serão criado cenario ideal
                vals = {
                    'manage_employee_time_id': self.id,
                    'punch_date': punch_ids.ids,
                    'punch_time': punch_time.ids,
                    'employee_id': self.employee_id.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'attention': 'warning' if len(punch_time) != 4 else 'info',
                    'week_day': day.strftime('%A').capitalize(),
                    'day': day
                }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)

            elif not justifications:#falta não justificada
                # verifica o proximo dsr pra ser descontado como falta dsr
                original_day = day
                while(day.strftime('%A').capitalize() != self.employee_id.dsr_week_days_id.day):
                    day += timedelta(days=1)
                if day not in dsr_lack:
                    dsr_lack.append(day)
                day = original_day

                #verifica se tem feriado pra descontar caso haja falta
                while (day.strftime('%A').capitalize() != 'Domingo'):
                    day += timedelta(days=1)
                sunday = day
                day = original_day
                while (day.strftime('%A').capitalize() != 'Segunda-feira'):
                    day -= timedelta(days=1)
                monday = day
                day = original_day

                # procura feriado no intervalo entre a segunda e o domingo
                punch_time_records = self.env['punch.time'].search([('id', 'in', records)])
                punch_time_records = punch_time_records.filtered(
                    lambda x: x.justification.hypothesis == 'Feriados' and x.day >= monday and x.day <= sunday)
                punch_time_records.write(
                    {'justification': self.env['remoteness'].search([('hypothesis', '=', 'Falta DSR')]).id,
                     'attention': 'danger',
                     })

                vals = {
                    'manage_employee_time_id': self.id,
                    'employee_id': self.employee_id.id,
                    'punch_date': punch_ids.ids,
                    'punch_time': punch_time.ids if punch_ids else False,
                    'justification': self.env['remoteness'].search([('hypothesis','=','Faltas não justificadas')]).id,
                    'attention': 'warning' if len(punch_time) != 4 else 'danger',
                    'week_day': day.strftime('%A').capitalize(),
                    'day': day
                }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)

            else:#se tiver justificativa
                vals = {
                    'manage_employee_time_id': self.id,
                    'employee_id': self.employee_id.id,
                    'justification': justifications[0].reason.id,
                    'attention': 'warning' if len(punch_time) != 4 else 'danger',
                    'week_day': day.strftime('%A').capitalize(),
                    'day': day
                }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)
            day += timedelta(days=1)

        #se houver falta de um dsr que não esta no range de pesquisa adiciona falta no proximo dsr
        for rec in dsr_lack:
            vals = {
                'manage_employee_time_id': self.id,
                'employee_id': self.employee_id.id,
                'justification': self.env['remoteness'].search([('hypothesis', '=', 'Falta DSR')]).id,
                'week_day': rec.strftime('%A').capitalize(),
                'attention': 'danger',
                'day': rec
            }
            record_created = self.env['punch.time'].create(vals)
            records.append(record_created.id)

        ctx = dict()
        ctx.update({
            'default_onchange_virtual_bank': True,
            'default_month': self.month,
            'default_year': self.year,
            'default_employee_id': self.employee_id.id,
            'default_punch_time_ids': records,
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
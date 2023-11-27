from datetime import datetime
from datetime import timedelta

from odoo import models, fields, api


class PunchClockIntegration(models.Model):
    _name = 'punch.clock'
    _rec_name = 'punch_date'

    original_afd_id = fields.Integer()
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    punch_date = fields.Date(string="Dia da Batida")
    punch_ids = fields.One2many('punch.clock.time', 'day_id', string="Horário das batidas", readonly=True)
    employee_pis = fields.Char("PIS")
    extra_night_hours = fields.Char(string="Hora extra noturna")
    nighttime_supplement = fields.Char(string="Adicional noturno")
    lunch_time = fields.Char(string="Horário de almoço", compute="compute_lunch_time")
    worked_hours = fields.Char(compute="compute_worked_hours", string="Horas trabalhadas")
    exit_earlier = fields.Char(string="Saída fora da jornada")
    hour_punch = fields.Integer()
    attears = fields.Char(string="Horas negativas", compute="compute_attears")
    extra_hour = fields.Char(string="Hora excedente", compute="compute_extra_hour")
    extra_hour_lunch = fields.Char(string="Hora extra almoço")
    interjourney = fields.Char(string="Interjornada")

    def punch_disregard(self):
        ctx = dict()
        punch_ids = self.punch_ids.filtered(lambda punch: punch.status != 'disregarded')
        ctx.update({
            'default_punch_clock_time_ids': punch_ids.ids,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Desconsideração de ponto',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'punch.disregard',
            'views': [[self.env.ref("punch_clock.punch_disregard_form_view").id, 'form']],
            'context': ctx,
            'target': 'new'
        }

    def deltatime_to_hours_minutes(self, deltatime):
        total_minutes_work = deltatime.days * 24 * 60 + deltatime.seconds // 60
        hours_work = total_minutes_work // 60
        minutes_work = total_minutes_work % 60
        return hours_work, minutes_work

    def open_wizard(self):
        ctx = dict()
        ctx.update({
            'default_day_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Criar apontamento manual',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.create.punch.time',
            'views': [[self.env.ref("punch_clock.wizard_create_punch_time_form").id, 'form']],
            'context': ctx,
            'target': 'new'
        }

    def create_punch_clock_time(self):
        vals = {
            'day_id': self.id,
            'hour_punch': self.hour_punch,
            'minute_punch': self.minute_punch,
        }
        self.env['punch.clock.time'].create(vals)

    def calculate_interjourney(self):
        for rec in self:
            punch_ids = rec.punch_ids.filtered(lambda punch: punch.status != 'disregarded')
            last_day = self.punch_date - timedelta(days=1)

            punch_ids_last = self.env['punch.clock.time'].search(
                [('day_id.employee_id', '=', rec.employee_id.id), ('day_id.punch_date', '=', last_day)])

            if len(punch_ids) > 0 and len(punch_ids_last) > 0:
                now = datetime.now()
                entrance_punch = punch_ids[0].time_punch.split(':')
                last_exit_time = punch_ids_last[-1].time_punch.split(':')
                punch_exit = datetime(year=now.year, month=now.month, day=now.day, hour=int(last_exit_time[0]),
                                      minute=int(last_exit_time[1]))
                punch_entrance = datetime(year=now.year, month=now.month, day=now.day, hour=int(entrance_punch[0]),
                                          minute=int(entrance_punch[1]))
                calc_interjourney = punch_entrance - punch_exit
                delta = timedelta(days=1)
                convert_interjourney = calc_interjourney + delta
                get_interjourney = timedelta(
                    hours=self.employee_id.general_configuration_id.interjourney) - convert_interjourney
                get_interjourney = str(get_interjourney).split(":")

                if convert_interjourney < timedelta(hours=self.employee_id.general_configuration_id.interjourney):
                    self.interjourney = "{:02d}:{:02d}".format(int(get_interjourney[0]), int(get_interjourney[1]))
                else:
                    self.interjourney = "{:02d}:{:02d}".format(0, 0)
            else:
                self.interjourney = "{:02d}:{:02d}".format(0, 0)

    def compute_extra_night(self):
        extra_hour_night = timedelta()
        start_night_time = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)
        for rec in self:
            punch_ids = rec.punch_ids.filtered(lambda punch: punch.status != 'disregarded')
            day_object = self.env['week.days'].search(
                [('day', 'ilike', self.punch_date.strftime('%A').capitalize())]).id
            departure_hour = ''
            entrance_time = ''
            for rec_workday in rec.employee_id.workday_id:
                if rec_workday.week_days_id.id == day_object:
                    departure_hour = rec_workday.departure_hour.time
                    entrance_time = rec_workday.entrance_hour.time
            if not departure_hour or not entrance_time:
                rec.extra_hour = "{:02d}:{:02d}".format(0, 0)
                return timedelta(0)

            if len(punch_ids) == 2 or len(punch_ids) == 4:
                departure_punch = punch_ids[-1].time_punch.split(':')
                now = datetime.now()
                punch_exit = datetime(year=now.year, month=now.month, day=now.day, hour=int(departure_punch[0]),
                                      minute=int(departure_punch[1]))

                if punch_exit > start_night_time:
                    extra_hour_night = punch_exit - start_night_time
                    format_night_hours = self.deltatime_to_hours_minutes(extra_hour_night)
                    self.extra_night_hours = "{:02d}:{:02d}".format(format_night_hours[0], format_night_hours[1])
                else:
                    self.extra_night_hours = "{:02d}:{:02d}".format(0, 0)
                return extra_hour_night
            else:
                self.extra_night_hours = "{:02d}:{:02d}".format(0, 0)
                return timedelta(0)

    def compute_extra_hour(self):
        for rec in self:
            punch_ids = rec.punch_ids.filtered(lambda punch: punch.status != 'disregarded')
            day_object = self.env['week.days'].search(
                [('day', 'ilike', rec.punch_date.strftime('%A').capitalize())]).id
            departure_hour = ''
            entrance_time = ''
            for rec_workday in rec.employee_id.workday_id:
                if rec_workday.week_days_id.id == day_object:
                    departure_hour = rec_workday.departure_hour.time
                    entrance_time = rec_workday.entrance_hour.time
            if not departure_hour or not entrance_time:
                rec.extra_hour = "{:02d}:{:02d}".format(0, 0)
                return timedelta(0)

            if len(punch_ids) == 2 and self.env['workday'].search(
                    [('week_days_id', '=', day_object), ('employee_id', '=', rec.employee_id.id)],
                    limit=1).intraday.__eq__(0):
                departure_punch = punch_ids[-1].time_punch.split(':')
                now = datetime.now()
                ideal_time = departure_hour.split(':')
                punch_exit = datetime(year=now.year, month=now.month, day=now.day, hour=int(departure_punch[0]),
                                      minute=int(departure_punch[1]))
                ideal_exit = datetime(year=now.year, month=now.month, day=now.day, hour=int(ideal_time[0]),
                                      minute=int(ideal_time[1]))

                entrance_punch = punch_ids[0].time_punch.split(':')
                ideal_entrance_config = entrance_time.split(':')
                ideal_entrance = datetime(year=now.year, month=now.month, day=now.day,
                                          hour=int(ideal_entrance_config[0]), minute=int(ideal_entrance_config[1]))
                punch_entrance = datetime(year=now.year, month=now.month, day=now.day, hour=int(entrance_punch[0]),
                                          minute=int(entrance_punch[1]))

                if ideal_entrance > punch_entrance:
                    arrive_early = ideal_entrance - punch_entrance
                else:
                    arrive_early = timedelta(0)

                if punch_exit > ideal_exit:
                    extra_hour = (punch_exit - ideal_exit) + arrive_early
                    extra_hour -= rec.compute_extra_night()
                    format_excess = rec.deltatime_to_hours_minutes(extra_hour)
                    rec.extra_hour = "{:02d}:{:02d}".format(format_excess[0], format_excess[1])
                    return extra_hour
                else:
                    format_excess = rec.deltatime_to_hours_minutes(arrive_early)
                    rec.extra_hour = "{:02d}:{:02d}".format(format_excess[0], format_excess[1])
                    return arrive_early

            elif len(punch_ids) == 4:
                departure_punch = punch_ids[-1].time_punch.split(':')
                now = datetime.now()
                ideal_time = departure_hour.split(':')
                punch_exit = datetime(year=now.year, month=now.month, day=now.day, hour=int(departure_punch[0]),
                                      minute=int(departure_punch[1]))
                ideal_exit = datetime(year=now.year, month=now.month, day=now.day, hour=int(ideal_time[0]),
                                      minute=int(ideal_time[1]))

                entrance_punch = punch_ids[0].time_punch.split(':')
                ideal_entrance_config = entrance_time.split(':')
                ideal_entrance = datetime(year=now.year, month=now.month, day=now.day,
                                          hour=int(ideal_entrance_config[0]), minute=int(ideal_entrance_config[1]))
                punch_entrance = datetime(year=now.year, month=now.month, day=now.day, hour=int(entrance_punch[0]),
                                          minute=int(entrance_punch[1]))

                if ideal_entrance > punch_entrance:
                    arrive_early = ideal_entrance - punch_entrance
                else:
                    arrive_early = timedelta(0)

                if punch_exit > ideal_exit:
                    extra_hour = (punch_exit - ideal_exit) + arrive_early
                    extra_hour -= rec.compute_extra_night()
                    format_excess = rec.deltatime_to_hours_minutes(extra_hour)
                    rec.extra_hour = "{:02d}:{:02d}".format(format_excess[0], format_excess[1])
                    return extra_hour
                else:
                    format_excess = rec.deltatime_to_hours_minutes(arrive_early)
                    rec.extra_hour = "{:02d}:{:02d}".format(format_excess[0], format_excess[1])
                    return arrive_early
            else:
                rec.extra_hour = "{:02d}:{:02d}".format(0, 0)
                return timedelta(0)

    def compute_attears(self):
        for rec in self:
            punch_ids = rec.punch_ids.filtered(lambda punch: punch.status != 'disregarded')
            day_object = self.env['week.days'].search(
                [('day', 'ilike', rec.punch_date.strftime('%A').capitalize())]).id
            entrance_time = ''
            departure_hour = ''
            for rec_workday in rec.employee_id.workday_id:
                if rec_workday.week_days_id.id == day_object:
                    entrance_time = rec_workday.entrance_hour.time
                    departure_hour = rec_workday.departure_hour.time
            if not entrance_time:
                rec.attears = "{:02d}:{:02d}".format(0, 0)
                return timedelta(0)
            if len(punch_ids) == 2 and self.env['workday'].search(
                    [('week_days_id', '=', day_object), ('employee_id', '=', self.employee_id.id)],
                    limit=1).intraday.__eq__(0):
                time = punch_ids[0].time_punch.split(':')
                ideal_time = entrance_time.split(':')
                date_time_1 = timedelta(hours=int(time[0]), minutes=int(time[1]))
                date_time_2 = timedelta(hours=int(ideal_time[0]), minutes=int(ideal_time[1]))

                time_exit = punch_ids[-1].time_punch.split(':')
                ideal_departure = departure_hour.split(':')
                punch_exit = timedelta(hours=int(time_exit[0]), minutes=int(time_exit[1]))
                ideal_exit = timedelta(hours=int(ideal_departure[0]), minutes=int(ideal_departure[1]))

                if date_time_1 > date_time_2:
                    arrears = date_time_1 - date_time_2
                else:
                    arrears = timedelta(0)

                if ideal_exit > punch_exit:
                    arrears += ideal_exit - punch_exit
                format_arrears = self.deltatime_to_hours_minutes(arrears)
                attears = "{:02d}:{:02d}".format(format_arrears[0], format_arrears[1])
                attears_hours, attears_minutes = map(int, attears.split(':')) if attears else 00
                attears_seconds = (attears_hours * 3600) + (attears_minutes * 60)

                rec.exit_earlier = "{:02d}:{:02d}".format(0, 0)
                # Cálculo total do atraso do funcionário, somando a entrada atrasada e a saída antecipada
                total_seconds = attears_seconds
                rec.attears = "{:02d}:{:02d}".format((total_seconds // 3600), ((total_seconds % 3600) // 60))
                return arrears

            elif len(punch_ids) == 4:
                time = punch_ids[0].time_punch.split(':')
                ideal_time = entrance_time.split(':')
                date_time_1 = timedelta(hours=int(time[0]), minutes=int(time[1]))
                date_time_2 = timedelta(hours=int(ideal_time[0]), minutes=int(ideal_time[1]))

                time_exit = punch_ids[-1].time_punch.split(':')
                ideal_departure = departure_hour.split(':')
                punch_exit = timedelta(hours=int(time_exit[0]), minutes=int(time_exit[1]))
                ideal_exit = timedelta(hours=int(ideal_departure[0]), minutes=int(ideal_departure[1]))

                if date_time_1 > date_time_2:
                    arrears = date_time_1 - date_time_2
                else:
                    arrears = timedelta(0)
                    
                if ideal_exit > punch_exit:
                    arrears += ideal_exit - punch_exit
                format_arrears = self.deltatime_to_hours_minutes(arrears)
                attears = "{:02d}:{:02d}".format(format_arrears[0], format_arrears[1])
                attears_hours, attears_minutes = map(int, attears.split(':')) if attears else 00
                attears_seconds = (attears_hours * 3600) + (attears_minutes * 60)

                # Atribuição de valores para as variáveis da saída antecipada do funcionário
                # if rec.exit_earlier != '00:00' and rec.exit_earlier != False:
                #     exit_earlier_hours, exit_earlier_minutes = map(int, rec.exit_earlier.split(':'))
                #     exit_earlier_seconds = (exit_earlier_hours * 3600) + (exit_earlier_minutes * 60)
                #     refactor_exit_earlier_hours = exit_earlier_seconds - attears_seconds
                #     total_seconds = attears_seconds + refactor_exit_earlier_hours
                #     rec.attears = "{:02d}:{:02d}".format((total_seconds // 3600), ((total_seconds % 3600) // 60))
                #     return arrears

                rec.exit_earlier = "{:02d}:{:02d}".format(0, 0)
                # Cálculo total do atraso do funcionário, somando a entrada atrasada e a saída antecipada
                total_seconds = attears_seconds
                rec.attears = "{:02d}:{:02d}".format((total_seconds // 3600), ((total_seconds % 3600) // 60))
                rec.calculate_tolerance_time()
                return arrears
            else:
                rec.attears = "{:02d}:{:02d}".format(0, 0)
                return timedelta(0)

    def compute_lunch_time(self):
        for rec in self:
            punch_ids = rec.punch_ids.filtered(lambda punch: punch.status != 'disregarded')
            lunch_period = 0
            day_object = self.env['week.days'].search(
                [('day', 'ilike', rec.punch_date.strftime('%A').capitalize())]).id
            for rec_day in self.employee_id.workday_id:
                if rec_day.week_days_id.id == day_object:
                    lunch_period = rec_day.intraday
            if lunch_period == 0:
                rec.lunch_time = "{:02d}:{:02d}".format(0, 0)
                return timedelta(0)
            if len(punch_ids) == 4:
                now = datetime.now()
                larger_hour = (len(punch_ids) / 2) + 1
                shorter_hour = len(punch_ids) / 2
                time_1 = punch_ids[int(shorter_hour - 1)].time_punch.split(':')
                time_2 = punch_ids[int(larger_hour - 1)].time_punch.split(':')
                date_time_1 = datetime(year=now.year, month=now.month, day=now.day, hour=int(time_1[0]),
                                       minute=int(time_1[1]))
                date_time_2 = datetime(year=now.year, month=now.month, day=now.day, hour=int(time_2[0]),
                                       minute=int(time_2[1]))
                lunch_time = date_time_2 - date_time_1
                if lunch_time <= timedelta(minutes=lunch_period):
                    extra_hour_lunch = timedelta(minutes=lunch_period) - lunch_time
                    format_extra_hour_lunch = rec.deltatime_to_hours_minutes(extra_hour_lunch)
                    rec.extra_hour_lunch = "{:02d}:{:02d}".format(format_extra_hour_lunch[0],
                                                                  format_extra_hour_lunch[1])
                else:
                    lunch_time_remove_extra_minutes = lunch_time - timedelta(minutes=lunch_period)
                    if rec.attears:
                        split_attears = rec.attears.split(':')
                        attears_timedelta = timedelta(hours=float(split_attears[0]), minutes=float(split_attears[1]))
                        format_attears = lunch_time_remove_extra_minutes + attears_timedelta
                        convert_to_string = str(format_attears).split(':')
                        rec.attears = "{:02d}:{:02d}".format(int(convert_to_string[0]), int(convert_to_string[1]))

                    rec.extra_hour_lunch = "{:02d}:{:02d}".format(00, 00)
                horas = lunch_time.seconds // 3600  # 1 hora = 3600 segundos
                minutos = (lunch_time.seconds % 3600) // 60
                rec.lunch_time = "{:02d}:{:02d}".format(horas, minutos)
                return lunch_time
            else:
                rec.lunch_time = "{:02d}:{:02d}".format(0, 0)
                rec.extra_hour_lunch = "{:02d}:{:02d}".format(0, 0)
                return timedelta(0)

    def calculate_tolerance_time(self):
        for record in self:
            punch_ids = record.punch_ids.filtered(lambda punch: punch.status != 'disregarded')
            if len(punch_ids) == 2 or len(punch_ids) == 4:
                day_object = self.env['week.days'].search(
                    [('day', 'ilike', record.punch_date.strftime('%A').capitalize())]).id
                if day_object:
                    entrance_time = ''
                    departure_hour = ''
                    for rec_workday in record.employee_id.workday_id:
                        if rec_workday.week_days_id.id == day_object:
                            entrance_time = rec_workday.entrance_hour.time.split(':')
                            departure_hour = rec_workday.departure_hour.time.split(':')

                    if entrance_time != '' and departure_hour != '':
                        ideal_entrance = timedelta(hours=int(entrance_time[0]), minutes=int(entrance_time[1]))
                        ideal_exit = timedelta(hours=int(departure_hour[0]), minutes=int(departure_hour[1]))
                        comp = timedelta()
                        for rec in self:
                            punch_ids = rec.punch_ids.filtered(lambda punch: punch.status != 'disregarded')
                            if len(punch_ids) > 1:
                                time_1 = punch_ids[0].time_punch.split(':')
                                time_2 = punch_ids[-1].time_punch.split(':')
                                date_time_1 = timedelta(hours=int(time_1[0]), minutes=int(time_1[1]))
                                date_time_2 = timedelta(hours=int(time_2[0]), minutes=int(time_2[1]))

                                if date_time_1 > ideal_entrance:
                                    comp = date_time_1 - ideal_entrance
                                elif date_time_1 < ideal_entrance:
                                    comp = ideal_entrance - date_time_1
                                if date_time_2 > ideal_exit:
                                    aux = date_time_2 - ideal_exit
                                    comp += aux
                                elif date_time_2 < ideal_exit:
                                    aux = ideal_exit - date_time_2
                                    comp += aux
                                if comp <= timedelta(minutes=self.employee_id.general_configuration_id.arrears_tolerance):
                                    rec.attears = "{:02d}:{:02d}".format(0, 0)
                                    rec.extra_hour = "{:02d}:{:02d}".format(0, 0)
                            else:
                                rec.attears = "{:02d}:{:02d}".format(0, 0)
                                rec.extra_hour = "{:02d}:{:02d}".format(0, 0)

    def compute_worked_hours(self):
        for record in self:
            punch_ids = record.punch_ids.filtered(lambda punch: punch.status != 'disregarded')
            now = datetime.now()
            start_night_time = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)
            worked_hours_in_day = timedelta()
            # verifica se as batidas são pares
            if len(punch_ids) % 2 == 0:
                # pega as batidas de entrada e saida e as subtrai, informando o
                # tempo entre as batidas e somando em "worked_hours"
                for i in range(0, len(punch_ids), 2):
                    if i + 1 < len(punch_ids):
                        time_1 = punch_ids[i].time_punch.split(':')
                        time_2 = punch_ids[i + 1].time_punch.split(':')
                        date_time_1 = datetime(year=now.year, month=now.month, day=now.day, hour=int(time_1[0]),
                                               minute=int(time_1[1]))
                        date_time_2 = datetime(year=now.year, month=now.month, day=now.day, hour=int(time_2[0]),
                                               minute=int(time_2[1]))
                        worked_hours_in_day += date_time_2 - date_time_1

                # record.compute_extra_hour()
                # record.calculate_tolerance_time()
                record.calculate_interjourney()
                # worked_hours_in_day -= record.compute_extra_night()

            horas = worked_hours_in_day.seconds // 3600  # 1 hora = 3600 segundos
            minutos = (worked_hours_in_day.seconds % 3600) // 60
            get_punch = punch_ids[0].time_punch.split(':')
            convert = datetime(year=now.year, month=now.month, day=now.day, hour=int(get_punch[0]),
                               minute=int(get_punch[1]))
            if convert >= start_night_time:
                record.nighttime_supplement = "{:02d}:{:02d}".format(horas, minutos)
                record.worked_hours = "{:02d}:{:02d}".format(0, 0)
            else:
                record.worked_hours = "{:02d}:{:02d}".format(horas, minutos)
                record.nighttime_supplement = "{:02d}:{:02d}".format(0, 0)
            return worked_hours_in_day
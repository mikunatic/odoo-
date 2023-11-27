from odoo import fields, models, api, _
from odoo.exceptions import UserError


class BankRegister(models.TransientModel):
    _name = 'bank.register'

    employee_id = fields.Many2one('hr.employee')
    extract_virtual_hours_id = fields.Many2one('extract.virtual.hours')
    punch_clock_id = fields.Many2one('punch.clock', string="Dia da Batida")
    punch_clock_time_ids = fields.Many2many('punch.clock.time', string="Batidas")
    date = fields.Date("Data")
    manage_employee_time_id = fields.Many2one('manage.employee.time')
    employees_by_interval_id = fields.Many2one('employees.by.interval')
    virtual_hours_lines_ids = fields.One2many('virtual.hours.lines', 'bank_register_id')
    extra_hour_lunch = fields.Char('Hora extra (intrajornada)')
    extra_hour = fields.Char('Horas excedentes')
    arrears_hour = fields.Char(related="punch_clock_id.attears", string='Atraso')
    lunch_time = fields.Char(related="punch_clock_id.lunch_time", string='Intrajornada')
    extra_night_hours = fields.Char(string="Hora extra noturna")
    nighttime_supplement = fields.Char(string="Adicional noturno")
    justification = fields.Char("Justificativa não remunerada")
    interjourney = fields.Char(string="Interjornada")

    def create_virtual_hours_line(self, event, total_hours):
        if total_hours and total_hours != "00:00":
            vals_list = {
                'bank_register_id': self.id,
                'events': event,
                'total_hours': total_hours,
            }
            self.env['virtual.hours.lines'].create(vals_list)

    @api.onchange('virtual_hours_lines_ids')
    def _onchange_virtual_hours_lines(self):
        if not self.virtual_hours_lines_ids:
            self.create_virtual_hours_line('credit', self.extra_hour)
            self.create_virtual_hours_line('credit', self.extra_hour_lunch)
            self.create_virtual_hours_line('debit', self.arrears_hour)
            self.create_virtual_hours_line('credit', self.extra_night_hours)
            self.create_virtual_hours_line('credit', self.nighttime_supplement)
            self.create_virtual_hours_line('credit', self.interjourney)
            self.create_virtual_hours_line('debit', self.justification)

    def confirm(self):
        # Atribuição em segundos para os créditos
        ideal_credit_hours = 0

        if self.extra_hour_lunch:
            extra_hour_lunch = self.extra_hour_lunch.split(":")
            ideal_credit_hours += ((int(extra_hour_lunch[0]) * 3600) + (int(extra_hour_lunch[1]) * 60))
        if self.extra_hour:
            extra_hour = self.extra_hour.split(":")
            ideal_credit_hours += ((int(extra_hour[0]) * 3600) + (int(extra_hour[1]) * 60))
        if self.extra_night_hours:
            extra_night_hours = self.extra_night_hours.split(":")
            ideal_credit_hours += ((int(extra_night_hours[0]) * 3600) + (int(extra_night_hours[1]) * 60))
        if self.nighttime_supplement:
            nighttime_supplement = self.nighttime_supplement.split(":")
            ideal_credit_hours += ((int(nighttime_supplement[0]) * 3600) + (int(nighttime_supplement[1]) * 60))
        if self.interjourney:
            interjourney = self.interjourney.split(":")
            ideal_credit_hours += ((int(interjourney[0]) * 3600) + (int(interjourney[1]) * 60))

        # Atribuição em segundos para os débitos
        ideal_debit_hours = 0

        if self.justification:
            justification = self.justification.split(":")
            ideal_debit_hours += ((int(justification[0]) * 3600) + (int(justification[1]) * 60))
        if self.arrears_hour:
            arrears_hour = self.arrears_hour.split(":")
            ideal_debit_hours += ((int(arrears_hour[0]) * 3600) + (int(arrears_hour[1]) * 60))

        debits_in_seconds = 0
        credits_in_seconds = 0
        punch_clock_time_ids = self.punch_clock_time_ids.filtered(lambda punch: punch.status != 'disregarded')
        for line in self.virtual_hours_lines_ids:
            # Validação para impedir do usuário não preencher os campos do banco virtual
            if line.events == 'debit' and not line.debit_virtual_bank_id or line.events == 'credit' and not line.credit_virtual_bank_id:
                raise UserError(_("Selecione o tipo de horas para a movimentação"))

            # Cálculo do saldo de horas da movimentação do funcionário
            employee_lines = self.env['extract.virtual.hours'].search([('employee_id','=',self.employee_id.id)])
            if not employee_lines:
                balance_in_seconds = line.total_hours.split(':')
                balance_in_seconds = (int(balance_in_seconds[0])*3600) + (int(balance_in_seconds[1])*60)
                if line.events == 'debit':
                    balance_in_seconds = balance_in_seconds * -1
                    debits_in_seconds += balance_in_seconds
                else:
                    balance_in_seconds = balance_in_seconds
                    credits_in_seconds += balance_in_seconds
            else:
                # Integer em segundos do saldo de horas linha de movimentação mais recente do funcionário
                last_line_seconds = employee_lines[0].balance_in_seconds

                # Integer em segundos das horas que entrarão para o banco
                hour_in_seconds = line.total_hours.split(':')
                hour_in_seconds = (int(hour_in_seconds[0]) * 3600) + (int(hour_in_seconds[1]) * 60)

                if line.events != 'debit':
                    # Crédito
                    balance_in_seconds = (last_line_seconds) + (hour_in_seconds)
                    credits_in_seconds += hour_in_seconds
                else:
                    balance_in_seconds = (last_line_seconds) - (hour_in_seconds)
                    debits_in_seconds += hour_in_seconds

            # Criação da linha de movimentação
            balance = "{:02d}:{:02d}".format(balance_in_seconds // 3600,(balance_in_seconds % 3600) // 60)
            movement_type = 'credit.virtual.bank, {}' if line.events != 'debit' else 'debit.virtual.bank, {}'
            format = line.credit_virtual_bank_id.id if line.events != 'debit' else line.debit_virtual_bank_id.id
            if not employee_lines:
                balance = line.total_hours
                if line.events == 'debit':
                    balance = "-"+balance
            vals_list = {
                'employee_id': self.employee_id.id,
                'date': self.date,
                'hours': line.total_hours,
                'movement_type': movement_type.format(format),
                'reference_bool': True if line.events != 'debit' else False,
                'balance_in_seconds': balance_in_seconds,
                'balance': balance,
            }
            self.env['extract.virtual.hours'].create(vals_list)

        week_day = self.date.strftime('%A').capitalize()
        workday = self.employee_id.workday_id.mapped('week_days_id').mapped('day')
        if len(punch_clock_time_ids) < 6 and week_day in workday or week_day in workday:
            #se os segundos ideais forem diferente dos segundos de todas as linhas, raise user error
            if debits_in_seconds != ideal_debit_hours or credits_in_seconds != ideal_credit_hours:
                raise UserError(_("Horas inseridas não batem com as horas ideais para o funcionário!"))

        # Write na linha do punch_time para que o usuário não faça movimentações no dia que já tem movimentações feitas
        punch_time_id = self.env[self.env.context.get("active_model")].browse(self.env.context.get("active_id"))
        punch_time_id.write({'allow_move_creation': False})

        # Retorno para a tela de pesquisa
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pesquisa de ponto',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manage.employee.time' if self.manage_employee_time_id else 'employees.by.interval',
            'res_id': self.manage_employee_time_id.id if self.manage_employee_time_id else self.employees_by_interval_id.id,
            'target': 'new',
        }

class VirtualHoursLines(models.TransientModel):
    _name = 'virtual.hours.lines'

    total_hours = fields.Char('Horas totais')
    bank_register_id = fields.Many2one('bank.register')
    events = fields.Selection([
        ('credit', 'Excedente'),
        ('debit', 'Devedora')
    ], default='credit', required=True, string='Evento')
    credit_virtual_bank_id = fields.Many2one(comodel_name="credit.virtual.bank", string='Crédito')
    debit_virtual_bank_id = fields.Many2one(comodel_name="debit.virtual.bank", string='Débito')
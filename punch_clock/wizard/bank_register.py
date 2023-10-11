from odoo import fields, models, api, _
from odoo.exceptions import UserError


class BankRegister(models.TransientModel):
    _name = 'bank.register'

    employee_id = fields.Many2one('hr.employee')
    extract_virtual_hours_id = fields.Many2one('extract.virtual.hours')
    punch_clock_time_ids = fields.Many2many('punch.clock.time', string="Batidas")
    date = fields.Date()
    manage_employee_time_id = fields.Many2one('manage.employee.time')
    virtual_hours_lines_ids = fields.One2many('virtual.hours.lines', 'bank_register_id')
    extra_hour_lunch = fields.Char('Hora extra (intrajornada)')
    extra_hour = fields.Char('Horas excedentes')
    arrears_hour = fields.Char('Atraso')
    extra_night_hours = fields.Char(string="Hora extra noturna")
    nighttime_supplement = fields.Char(string="Adicional noturno")

    @api.onchange('virtual_hours_lines_ids')
    def _onchange_virtual_hours_lines(self):
        if not self.virtual_hours_lines_ids:
            if self.extra_hour != "00:00" and self.extra_hour != False:
                extra_hours_vals_list = {
                    'bank_register_id':self.id,
                    'events': 'credit',
                    'total_hours': self.extra_hour,
                }
                self.env['virtual.hours.lines'].create(extra_hours_vals_list)

            if self.extra_hour_lunch != "00:00" and self.extra_hour_lunch != False:
                extra_hours_lunch_vals_list = {
                    'bank_register_id': self.id,
                    'events': 'intra',
                    'total_hours': self.extra_hour_lunch,
                }
                self.env['virtual.hours.lines'].create(extra_hours_lunch_vals_list)

            if self.arrears_hour != "00:00" and self.arrears_hour != False:
                arrears_hour_vals_list = {
                    'bank_register_id': self.id,
                    'events': 'debit',
                    'total_hours': self.arrears_hour,
                }
                self.env['virtual.hours.lines'].create(arrears_hour_vals_list)

            if self.extra_night_hours != "00:00" and self.extra_night_hours != False:
                extra_night_hours_vals_list = {
                    'bank_register_id':self.id,
                    'events': 'credit',
                    'total_hours': self.extra_night_hours,
                }
                self.env['virtual.hours.lines'].create(extra_night_hours_vals_list)

            if self.nighttime_supplement != "00:00" and self.nighttime_supplement != False:
                nighttime_supplement_vals_list = {
                    'bank_register_id':self.id,
                    'events': 'credit',
                    'total_hours': self.nighttime_supplement,
                }
                self.env['virtual.hours.lines'].create(nighttime_supplement_vals_list)

    def confirm(self):
        for line in self.virtual_hours_lines_ids:
            # Validação para impedir do usuário passar despercebido pelas informações e não preencher os campos do banco virtual
            if line.events == 'debit' and not line.debit_virtual_bank_id or line.events == 'credit' and not line.credit_virtual_bank_id:
                raise UserError(_("Selecione o tipo de horas para a movimentação"))

            # Cálculo das saldo de horas da movimentação do funcionário
            employee_lines = self.env['extract.virtual.hours'].search([('employee_id','=',self.employee_id.id)])
            if not employee_lines:
                balance_in_seconds = line.total_hours.split(':')
                balance_in_seconds = (int(balance_in_seconds[0])*3600) + (int(balance_in_seconds[1])*60)
                if line.events == 'debit':
                    balance_in_seconds = balance_in_seconds * -1
                else:
                    balance_in_seconds = balance_in_seconds
            else:
                # Integer em segundos do saldo de horas linha de movimentação mais recente do funcionário
                last_line_seconds = employee_lines[0].balance_in_seconds

                # Integer em segundos das horas que entrarão para o banco
                hour_in_seconds = line.total_hours.split(':')
                hour_in_seconds = (int(hour_in_seconds[0]) * 3600) + (int(hour_in_seconds[1]) * 60)

                if line.events != 'debit':
                    balance_in_seconds = (last_line_seconds) + (hour_in_seconds)
                else:
                    balance_in_seconds = (last_line_seconds) - (hour_in_seconds)

            # Criação da linha de movimentação
            balance = str(balance_in_seconds // 3600) + ":" + str((balance_in_seconds % 3600) // 60)
            movement_type = 'credit.virtual.bank, {}' if line.events != 'debit' else 'debit.virtual.bank, {}'
            format = line.credit_virtual_bank_id.id if line.events != 'debit' else line.debit_virtual_bank_id.id
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

        # Write na linha do punch_time para que o usuário não faça movimentações no dia que já tem movimentações feitas
        punch_time_id = self.env[self.env.context.get("active_model")].browse(self.env.context.get("active_id"))
        punch_time_id.write({'allow_move_creation': False})

        # Retorno para a tela de pesquisa
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pesquisa de ponto',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manage.employee.time',
            'res_id': self.manage_employee_time_id.id,
            # 'views': [[self.env.ref("punch_clock.manage_employee_time_form").id,'tree']],
            'target': 'new'
        }

class VirtualHoursLines(models.TransientModel):
    _name = 'virtual.hours.lines'

    total_hours = fields.Char('Horas totais')
    bank_register_id = fields.Many2one('bank.register')
    events = fields.Selection([
        ('intra', 'Intrajornada'),
        ('credit', 'Excedente'),
        ('debit', 'Atraso')
    ], default='credit', required=True, string='Evento')
    credit_virtual_bank_id = fields.Many2one(comodel_name="credit.virtual.bank", string='Crédito')
    debit_virtual_bank_id = fields.Many2one(comodel_name="debit.virtual.bank", string='Débito')

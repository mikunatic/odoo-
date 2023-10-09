from odoo import fields, models


class AddEvent(models.Model):
    _name = 'add.event'

    date = fields.Date("Dia", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Funcionário", readonly=True)
    punch_clock_time_ids = fields.Many2many('punch.clock.time', string="Horários das batidas", readonly=True)

    arrears = fields.Char("Atraso", readonly=True)
    arrears_movement = fields.Many2one('debit.virtual.bank', string="Débito")

    extra_hour = fields.Char("Hora excedente", readonly=True)
    extra_hour_movement = fields.Many2one('credit.virtual.bank', string="Crédito")

    extra_hour_lunch = fields.Char("Hora Extra (almoço)", readonly=True)
    extra_hour_lunch_movement = fields.Many2one('credit.virtual.bank', string="Crédito")

    def create_move(self):
        # Criação para caso haja atraso
        if self.arrears != '00:00' and self.arrears != False:
            arrears_vals_list = {
                'date': self.date,
                'hours': self.arrears,
                'employee_id': self.employee_id.id,
                'movement_type': 'debit.virtual.bank, {}'.format(self.arrears_movement.id),
                'reference_bool': False,
            }
            self.env['virtual.bank'].create(arrears_vals_list)

        # Criação para caso haja horas excedentes
        if self.extra_hour != '00:00' and self.extra_hour != False:
            extra_hour_vals_list = {
                'date': self.date,
                'hours': self.extra_hour,
                'employee_id': self.employee_id.id,
                'movement_type': 'credit.virtual.bank, {}'.format(self.extra_hour_movement.id),
                'reference_bool': True,
            }
            self.env['virtual.bank'].create(extra_hour_vals_list)

        # Criação para caso haja hora extra de almoço
        if self.extra_hour_lunch != '00:00' and self.extra_hour_lunch != False:
            extra_hour_lunch_vals_list = {
                'date': self.date,
                'hours': self.extra_hour_lunch,
                'employee_id': self.employee_id.id,
                'movement_type': 'credit.virtual.bank, {}'.format(self.extra_hour_lunch_movement.id),
                'reference_bool': True,
            }
            self.env['virtual.bank'].create(extra_hour_lunch_vals_list)

        # Retorno para a tela de pesquisa
        #pegando id do punch time, fazer com que pegue o id da tela de pesquisa
        res_id = self.env.context.get("active_id")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pesquisa de ponto',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manage.employee.time',
            'res_id': res_id,
            # 'views': [[self.env.ref("punch_clock.manage_employee_time_form").id, 'form']],
            'target': 'new',
            'ctx': self.env.context
        }
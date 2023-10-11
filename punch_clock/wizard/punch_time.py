from odoo import models, fields


class PunchTime(models.TransientModel):
    _name = 'punch.time'

    manage_employee_time_id = fields.Many2one('manage.employee.time')
    employees_by_interval_id = fields.Many2one('employees.by.interval')
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    punch_date = fields.Many2many('punch.clock', string="Batidas")
    punch_time = fields.Many2many('punch.clock.time', string="Batidas")
    worked_hour_related = fields.Char(related="punch_date.worked_hours", string="Trabalho")
    lunch_time_related = fields.Char(related="punch_date.lunch_time")
    attears_hour_related = fields.Char(related="punch_date.attears")
    extra_hour_hour_related = fields.Char(related="punch_date.extra_hour")
    employee_pis = fields.Char(string="PIS do Funcionário")
    justification = fields.Many2one('remoteness', string="Justificativa")
    week_day = fields.Char(string='Dia da semana')
    day = fields.Date(string='Dia')
    attention = fields.Selection(
        [('warning', 'Atenção'), ('success', 'Sucesso'), ('info', 'Info'), ('danger', 'Danger')])
    allow_move_creation = fields.Boolean()

    def return_extra_hours(self):
        ctx = {
            'default_employee_id': self.manage_employee_time_id.employee_id.id,
            'default_date': self.day,
            'default_punch_clock_time_ids': self.punch_time.ids,
            'default_extra_hour_lunch': self.punch_date.extra_hour_lunch,
            'default_extra_hour': self.punch_date.extra_hour,
            'default_arrears_hour': self.punch_date.attears,
            'default_extra_night_hours': self.punch_date.attears,
            'default_nighttime_supplement': self.punch_date.attears,
            'default_manage_employee_time_id': self.manage_employee_time_id.id,
        }
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

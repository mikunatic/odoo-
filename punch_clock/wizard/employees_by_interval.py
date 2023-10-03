from odoo import models, fields, _, api
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import date


class EmployeesByInterval(models.TransientModel):
    _name = 'employees.by.interval'

    inicial_day_to_search = fields.Date(string="Dia", required=True)
    final_day_to_search = fields.Date(string="Dia final")
    employee_id = fields.Many2one('hr.employee')
    employee_company = fields.Many2one('employee.company', string="Empresa")
    employee_department = fields.Many2one('hr.department', string="Departamento")
    search_filter = fields.Selection([('department', 'Departamento'),
                                      ('company', 'Empresa'),
                                      ('department_company', 'Departamento e empresa')], string="Filtro de pesquisa")
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
    punch_time_ids = fields.One2many('punch.time', 'employees_by_interval_id', string="Horarios")

    def search_employees(self):
        records = []
        if self.search_filter == 'department':
            if self.punch_time_ids:
                self.punch_time_ids.unlink()
            punch_clock_ids = self.env['punch.clock'].search(
                [('punch_date', '=', self.inicial_day_to_search)])
            punch_clock_ids = punch_clock_ids.filtered(lambda x: x.employee_id.department_id.id == self.employee_department.id)
            punch_ids_date = punch_clock_ids.mapped('punch_date')
            holiday = self.env['holiday'].search([('inicial_date', '=', self.inicial_day_to_search)])
            search_justifications = self.env['employee.remoteness'].search(
                [('initial_date', '<=', self.inicial_day_to_search), ('final_date', '>=', self.inicial_day_to_search)])
            for rec in punch_clock_ids:
                justifications = search_justifications.filtered(lambda x: x.employee_id.id == rec.employee_id.id)
                punch_ids = self.env['punch.clock'].search(
                    [('punch_date', '=', rec.punch_date), ('employee_id', '=', rec.employee_id.id)])
                punch_time = self.env['punch.clock.time'].search([('day_id', '=', punch_ids.id)])
                is_holiday = holiday.filtered(lambda x: rec.punch_date <= x.final_date and rec.punch_date >= x.inicial_date)
                if rec.employee_id.id in holiday.employees_ids.ids:
                    vals = {
                        'employees_by_interval_id': self.id,
                        'punch_date': punch_ids.ids,
                        'punch_time': punch_time.ids,
                        'employee_id': rec.employee_id.id,
                        'justification': 3,
                        'attention': 'success',
                        'week_day': rec.punch_date.strftime('%A').capitalize(),
                        'day': rec.punch_date
                    }

                else:
                    vals = {
                        'employees_by_interval_id': self.id,
                        'punch_date': punch_ids.ids,
                        'punch_time': punch_time.ids,
                        'employee_id': rec.employee_id.id,
                        'employee_pis': rec.employee_id.employee_pis,
                        'justification': justifications[0].reason.id if justifications else False,
                        'attention': 'warning' if len(punch_time) < 4 else 'info',
                        'week_day': rec.punch_date.strftime('%A').capitalize(),
                        'day': rec.punch_date
                    }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)

            ctx = dict()
            ctx.update({
                'default_inicial_day_to_search': self.inicial_day_to_search,
                'default_punch_time_ids': records,
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pesquisa de ponto',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'employees.by.interval',
                'views': [[self.env.ref("punch_clock.employees_by_interval_form").id, 'form']],
                'context': ctx,
                'target': 'new'
            }

        elif self.search_filter == 'company':
            if self.punch_time_ids:
                self.punch_time_ids.unlink()
            punch_clock_ids = self.env['punch.clock'].search(
                [('punch_date', '=', self.inicial_day_to_search)])
            punch_clock_ids = punch_clock_ids.filtered(lambda x: x.employee_id.company_id.id == self.employee_company.id)
            punch_ids_date = punch_clock_ids.mapped('punch_date')
            holiday = self.env['holiday'].search([('inicial_date', '=', self.inicial_day_to_search)])
            search_justifications = self.env['employee.remoteness'].search(
                [('initial_date', '<=', self.inicial_day_to_search), ('final_date', '>=', self.inicial_day_to_search)])
            for rec in punch_clock_ids:
                justifications = search_justifications.filtered(lambda x: x.employee_id.id == rec.employee_id.id)
                punch_ids = self.env['punch.clock'].search(
                    [('punch_date', '=', rec.punch_date), ('employee_id', '=', rec.employee_id.id)])
                punch_time = self.env['punch.clock.time'].search([('day_id', '=', punch_ids.id)])
                is_holiday = holiday.filtered(
                    lambda x: rec.punch_date <= x.final_date and rec.punch_date >= x.inicial_date)
                if rec.employee_id.id in holiday.employees_ids.ids:
                    vals = {
                        'employees_by_interval_id': self.id,
                        'punch_date': punch_ids.ids,
                        'punch_time': punch_time.ids,
                        'employee_id': rec.employee_id.id,
                        'justification': 3,
                        'attention': 'success',
                        'week_day': rec.punch_date.strftime('%A').capitalize(),
                        'day': rec.punch_date
                    }
                else:
                    vals = {
                        'employees_by_interval_id': self.id,
                        'punch_date': punch_ids.ids,
                        'punch_time': punch_time.ids,
                        'employee_id': rec.employee_id.id,
                        'employee_pis': rec.employee_id.employee_pis,
                        'justification': justifications[0].reason.id if justifications else False,
                        'attention': 'warning' if len(punch_time) < 4 else 'info',
                        'week_day': rec.punch_date.strftime('%A').capitalize(),
                        'day': rec.punch_date
                    }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)

            ctx = dict()
            ctx.update({
                'default_inicial_day_to_search': self.inicial_day_to_search,
                'default_punch_time_ids': records,
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pesquisa de ponto',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'employees.by.interval',
                'views': [[self.env.ref("punch_clock.employees_by_interval_form").id, 'form']],
                'context': ctx,
                'target': 'new'
            }

        elif self.search_filter == 'department_company':
            if self.punch_time_ids:
                self.punch_time_ids.unlink()
            punch_clock_ids = self.env['punch.clock'].search(
                [('punch_date', '=', self.inicial_day_to_search)])
            punch_clock_ids = punch_clock_ids.filtered(
                lambda x: x.employee_id.department_id.id == self.employee_department.id and x.employee_id.company_id.id == self.employee_company.id)
            punch_ids_date = punch_clock_ids.mapped('punch_date')
            holiday = self.env['holiday'].search([('inicial_date', '=', self.inicial_day_to_search)])
            search_justifications = self.env['employee.remoteness'].search(
                [('initial_date', '<=', self.inicial_day_to_search), ('final_date', '>=', self.inicial_day_to_search)])
            for rec in punch_clock_ids:
                justifications = search_justifications.filtered(lambda x: x.employee_id.id == rec.employee_id.id)
                punch_ids = self.env['punch.clock'].search(
                    [('punch_date', '=', rec.punch_date), ('employee_id', '=', rec.employee_id.id)])
                punch_time = self.env['punch.clock.time'].search([('day_id', '=', punch_ids.id)])
                is_holiday = holiday.filtered(
                    lambda x: rec.punch_date <= x.final_date and rec.punch_date >= x.inicial_date)
                if rec.employee_id.id in holiday.employees_ids.ids:
                    vals = {
                        'employees_by_interval_id': self.id,
                        'punch_date': punch_ids.ids,
                        'punch_time': punch_time.ids,
                        'employee_id': rec.employee_id.id,
                        'justification': 3,
                        'attention': 'success',
                        'week_day': rec.punch_date.strftime('%A').capitalize(),
                        'day': rec.punch_date
                    }
                else:
                    vals = {
                        'employees_by_interval_id': self.id,
                        'punch_date': punch_ids.ids,
                        'punch_time': punch_time.ids,
                        'employee_id': rec.employee_id.id,
                        'employee_pis': rec.employee_id.employee_pis,
                        'justification': justifications[0].reason.id if justifications else False,
                        'attention': 'warning' if len(punch_time) < 4 else 'info',
                        'week_day': rec.punch_date.strftime('%A').capitalize(),
                        'day': rec.punch_date
                    }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)

            ctx = dict()
            ctx.update({
                'default_inicial_day_to_search': self.inicial_day_to_search,
                'default_punch_time_ids': records,
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pesquisa de ponto',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'employees.by.interval',
                'views': [[self.env.ref("punch_clock.employees_by_interval_form").id, 'form']],
                'context': ctx,
                'target': 'new'
            }

        else:
            if self.punch_time_ids:
                self.punch_time_ids.unlink()
            punch_clock_ids = self.env['punch.clock'].search(
                [('punch_date', '=', self.inicial_day_to_search)])
            punch_ids_date = punch_clock_ids.mapped('punch_date')
            holiday = self.env['holiday'].search([('inicial_date', '=', self.inicial_day_to_search)])
            search_justifications = self.env['employee.remoteness'].search([('initial_date', '<=', self.inicial_day_to_search), ('final_date', '>=', self.inicial_day_to_search)])

            for rec in punch_clock_ids:
                justifications = search_justifications.filtered(lambda x: x.employee_id.id == rec.employee_id.id)
                punch_ids = self.env['punch.clock'].search(
                    [('punch_date', '=', rec.punch_date), ('employee_id', '=', rec.employee_id.id)])
                punch_time = self.env['punch.clock.time'].search([('day_id', '=', punch_ids.id)])
                if rec.employee_id.id in holiday.employees_ids.ids:
                    vals = {
                        'employees_by_interval_id': self.id,
                        'punch_date': punch_ids.ids,
                        'punch_time': punch_time.ids,
                        'employee_id': rec.employee_id.id,
                        'justification': 3,
                        'attention': 'success',
                        'week_day': rec.punch_date.strftime('%A').capitalize(),
                        'day': rec.punch_date
                    }
                else:
                    vals = {
                        'employees_by_interval_id': self.id,
                        'punch_date': punch_ids.ids,
                        'punch_time': punch_time.ids,
                        'employee_id': rec.employee_id.id,
                        'employee_pis': rec.employee_id.employee_pis,
                        'justification': justifications[0].reason.id if justifications else False,
                        'attention': 'warning' if len(punch_time) < 4 else 'info',
                        'week_day': rec.punch_date.strftime('%A').capitalize(),
                        'day': rec.punch_date
                    }
                record_created = self.env['punch.time'].create(vals)
                records.append(record_created.id)
            ctx = dict()
            ctx.update({
                'default_inicial_day_to_search': self.inicial_day_to_search,
                'default_punch_time_ids': records,
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pesquisa de ponto',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'employees.by.interval',
                'views': [[self.env.ref("punch_clock.employees_by_interval_form").id, 'form']],
                'context': ctx,
                'target': 'new'
            }


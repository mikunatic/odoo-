from odoo import models, fields
from datetime import date


class EmployeesByInterval(models.TransientModel):
    _name = 'employees.by.interval'

    day_to_search = fields.Date(string="Dia", required=True)
    employee_company = fields.Many2one('employee.company', string="Empresa")
    employee_department = fields.Many2one('hr.department', string="Departamento")
    search_filter = fields.Selection([('department', 'Departamento'),
                                      ('company', 'Empresa'),
                                      ('department_company', 'Departamento e empresa')],
                                     string="Filtro de pesquisa", required=True )
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
        # Declaração de variáveis
        convert_to_week_day = self.day_to_search.strftime('%A').capitalize()
        dsr = self.env['hr.employee'].search([('dsr_week_days_id', '=like', convert_to_week_day)])
        punch_ids = self.env['punch.clock'].search(
            [('punch_date', '=', self.day_to_search)]).mapped('employee_id')
        punch_clock_ids = self.env['punch.clock'].search(
            [('punch_date', '=', self.day_to_search)])
        search_justifications = self.env['employee.remoteness'].search(
            [('initial_date', '<=', self.day_to_search), ('final_date', '>=', self.day_to_search)])

        if self.punch_time_ids:
            self.punch_time_ids.unlink()

        if self.search_filter == 'department':
            week_days_ids = self.env['workday'].search(
                [('week_days_id', '=',
                  self.env['week.days'].search([('day', '=like', convert_to_week_day)]).id)]).mapped(
                'employee_id').filtered(lambda lm: lm.department_id.id == self.employee_department.id)

            non_presence_employee = week_days_ids.filtered(lambda lm: lm.id not in punch_ids.ids)
            # Pesquisando os pontos de acordo com o filtro
            punch_clock_ids = punch_clock_ids.filtered(
                lambda x: x.employee_id.department_id.id == self.employee_department.id)

            for rec in punch_clock_ids:
                virtual_bank_move = self.env['extract.virtual.hours'].search([
                    ('employee_id', '=', rec.employee_id.id), ('date', '=', self.day_to_search)])
                justifications = search_justifications.filtered(
                    lambda remoteness: remoteness.employee_remoteness_ids.id == rec.employee_id.id)
                punch_ids = self.env['punch.clock'].search(
                    [('punch_date', '=', rec.punch_date), ('employee_id', '=', rec.employee_id.id)])
                punch_time = self.env['punch.clock.time'].search([('day_id', '=', punch_ids.id)])
                vals = {
                    'employees_by_interval_id': self.id,
                    'punch_date': punch_ids.id,
                    'punch_time': punch_time.ids,
                    'employee_id': rec.employee_id.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'week_day': convert_to_week_day,
                    'day': rec.punch_date,
                    'allow_move_creation': True if not virtual_bank_move else False,
                }
                self.env['punch.time'].create(vals)

            for rec in dsr:
                virtual_bank_move = self.env['extract.virtual.hours'].search([
                    ('employee_id', '=', rec.id), ('date', '=', self.day_to_search)])
                justifications = search_justifications.filtered(
                    lambda remoteness: rec.id in remoteness.employee_remoteness_ids.ids)
                vals = {
                    'employees_by_interval_id': self.id,
                    'employee_id': rec.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'week_day': convert_to_week_day,
                    'day': self.day_to_search,
                    'allow_move_creation': True if not virtual_bank_move else False,
                }
                self.env['punch.time'].create(vals)

            for rec in non_presence_employee:
                virtual_bank_move = self.env['extract.virtual.hours'].search([
                    ('employee_id', '=', rec.id), ('date', '=', self.day_to_search)])
                justifications = search_justifications.filtered(
                    lambda remoteness: rec.id in remoteness.employee_remoteness_ids.ids)
                vals = {
                    'employees_by_interval_id': self.id,
                    'employee_id': rec.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'week_day': convert_to_week_day,
                    'day': self.day_to_search,
                    'allow_move_creation': True if not virtual_bank_move else False,
                }
                self.env['punch.time'].create(vals)

        elif self.search_filter == 'company':
            week_days_ids = self.env['workday'].search(
                [('week_days_id', '=',
                  self.env['week.days'].search([('day', '=like', convert_to_week_day)]).id)]).mapped(
                'employee_id').filtered(lambda lm: lm.company_inherit.id == self.employee_company.id)

            non_presence_employee = week_days_ids.filtered(lambda lm: lm.id not in punch_ids.ids)
            # Pesquisando os pontos de acordo com o filtro
            punch_clock_ids = punch_clock_ids.filtered(
                lambda x: x.employee_id.company_inherit.id == self.employee_company.id)

            for rec in punch_clock_ids:
                virtual_bank_move = self.env['extract.virtual.hours'].search([
                    ('employee_id', '=', rec.employee_id.id), ('date', '=', self.day_to_search)])
                justifications = search_justifications.filtered(
                    lambda remoteness: remoteness.employee_remoteness_ids.id == rec.employee_id.id)
                punch_ids = self.env['punch.clock'].search(
                    [('punch_date', '=', rec.punch_date), ('employee_id', '=', rec.employee_id.id)])
                punch_time = self.env['punch.clock.time'].search([('day_id', '=', punch_ids.id)])
                vals = {
                    'employees_by_interval_id': self.id,
                    'punch_date': punch_ids.id,
                    'punch_time': punch_time.ids,
                    'employee_id': rec.employee_id.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'week_day': convert_to_week_day,
                    'day': rec.punch_date,
                    'allow_move_creation': True if not virtual_bank_move else False,
                }
                self.env['punch.time'].create(vals)

            for rec in dsr:
                virtual_bank_move = self.env['extract.virtual.hours'].search([
                    ('employee_id', '=', rec.id), ('date', '=', self.day_to_search)])
                justifications = search_justifications.filtered(
                    lambda remoteness: rec.id in remoteness.employee_remoteness_ids.ids)
                vals = {
                    'employees_by_interval_id': self.id,
                    'employee_id': rec.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'week_day': convert_to_week_day,
                    'day': self.day_to_search,
                    'allow_move_creation': True if not virtual_bank_move else False,
                }
                self.env['punch.time'].create(vals)

            for rec in non_presence_employee:
                virtual_bank_move = self.env['extract.virtual.hours'].search([
                    ('employee_id', '=', rec.id), ('date', '=', self.day_to_search)])
                justifications = search_justifications.filtered(
                    lambda remoteness: rec.id in remoteness.employee_remoteness_ids.ids)
                vals = {
                    'employees_by_interval_id': self.id,
                    'employee_id': rec.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'week_day': convert_to_week_day,
                    'day': self.day_to_search,
                    'allow_move_creation': True if not virtual_bank_move else False,
                }
                self.env['punch.time'].create(vals)

        elif self.search_filter == 'department_company':
            week_days_ids = self.env['workday'].search(
                [('week_days_id', '=',
                  self.env['week.days'].search([('day', '=like', convert_to_week_day)]).id)]).mapped(
                'employee_id').filtered(lambda x: x.department_id.id == self.employee_department.id and x.company_inherit.id == self.employee_company.id)
            non_presence_employee = week_days_ids.filtered(lambda lm: lm.id not in punch_ids.ids)

            # Pesquisando os pontos de acordo com o filtro
            punch_clock_ids = punch_clock_ids.filtered(lambda x: x.employee_id.department_id.id == self.employee_department.id and x.employee_id.company_inherit.id == self.employee_company.id)
            for rec in punch_clock_ids:
                virtual_bank_move = self.env['extract.virtual.hours'].search([
                    ('employee_id', '=', rec.employee_id.id), ('date', '=', self.day_to_search)])
                justifications = search_justifications.filtered(
                    lambda remoteness: remoteness.employee_remoteness_ids.ids == rec.employee_id.id)
                punch_ids = self.env['punch.clock'].search(
                    [('punch_date', '=', rec.punch_date), ('employee_id', '=', rec.employee_id.id)])
                punch_time = self.env['punch.clock.time'].search([('day_id', '=', punch_ids.id)])
                vals = {
                    'employees_by_interval_id': self.id,
                    'punch_date': punch_ids.id,
                    'punch_time': punch_time.ids,
                    'employee_id': rec.employee_id.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'week_day': convert_to_week_day,
                    'day': rec.punch_date,
                    'allow_move_creation': True if not virtual_bank_move else False,
                }
                self.env['punch.time'].create(vals)

            for rec in dsr:
                virtual_bank_move = self.env['extract.virtual.hours'].search([
                    ('employee_id', '=', rec.id), ('date', '=', self.day_to_search)])
                justifications = search_justifications.filtered(
                    lambda remoteness: rec.id in remoteness.employee_remoteness_ids.ids)
                vals = {
                    'employees_by_interval_id': self.id,
                    'employee_id': rec.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'week_day': convert_to_week_day,
                    'day': self.day_to_search,
                    'allow_move_creation': True if not virtual_bank_move else False,
                }
                self.env['punch.time'].create(vals)

            for rec in non_presence_employee:
                virtual_bank_move = self.env['extract.virtual.hours'].search([
                    ('employee_id', '=', rec.id), ('date', '=', self.day_to_search)])
                justifications = search_justifications.filtered(
                    lambda remoteness: rec.id in remoteness.employee_remoteness_ids.ids)
                vals = {
                    'employees_by_interval_id': self.id,
                    'employee_id': rec.id,
                    'justification': justifications[0].reason.id if justifications else False,
                    'week_day': convert_to_week_day,
                    'day': self.day_to_search,
                    'allow_move_creation': True if not virtual_bank_move else False,
                }
                self.env['punch.time'].create(vals)

        ctx = dict()
        ctx.update({
            'default_day_to_search': self.day_to_search,
            'default_punch_time_ids': self.punch_time_ids.ids,
            'default_search_filter': self.search_filter,
            'default_employee_department': self.employee_department.id if self.employee_department else False,
            'default_employee_company': self.employee_company.id if self.employee_company else False,
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
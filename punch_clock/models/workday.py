from odoo import fields, models, api


class Workday(models.Model):
    _name = 'workday'

    entrance_hour = fields.Many2one('hour', string="Hora de Entrada")
    departure_hour = fields.Many2one('hour', string="Hora de Saída")
    week_days_id = fields.Many2one('week.days', string="Dias da semana")
    employee_id = fields.Many2one('hr.employee')
    intraday = fields.Integer("Intrajornada")

    @api.model
    def create_journey(self):
        employee_ids = self.env['hr.employee'].search([])
        for employee in employee_ids:
            for day in range(2, 7):
                vals = {
                    'entrance_hour': self.env['hour'].search([('time','=','08:00')]).id,
                    'departure_hour': self.env['hour'].search([('time','=','17:00')]).id,
                    'week_days_id': day,
                    'employee_id': employee.id,
                    'intraday': 60,
                }
                self.env['workday'].create(vals)
            vals_no_intraday = {
                'entrance_hour':  self.env['hour'].search([('time','=','08:00')]).id,
                'departure_hour':  self.env['hour'].search([('time','=','12:00')]).id,
                'week_days_id': 7,
                'employee_id': employee.id,
                'intraday': 0,
            }
            self.env['workday'].create(vals_no_intraday)
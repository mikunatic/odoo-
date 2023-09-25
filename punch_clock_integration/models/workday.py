from odoo import fields, models


class Workday(models.Model):
    _name = 'workday'

    hour_ids = fields.Many2many('hour', string="Horas a trabalhar")
    week_days_id = fields.Many2one('week.days', string="Dias da semana")
    employee_id = fields.Many2one('hr.employee')
    intraday = fields.Boolean("Intrajornada")

    # saturday = fields.Selection([('weekly','Semanal'),('fortnightly','Quinzenal'),('monthly','Mensal'),('never','Nunca')], string="Sábado")

    # def name_get(self):
    #     return [(rec.id, str(rec.weekly_hours)+" horas semanais"+"/"+str(rec.work_week_days)+" dias da semana") for rec in self]
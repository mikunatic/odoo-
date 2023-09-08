from odoo import models, fields, api


class PunchClockIntegration(models.Model):
    _name = 'punch.clock'
    _rec_name = 'punch_datetime'

    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    punch_datetime = fields.Datetime("Horário da Batida")
    punch_id = fields.Integer()
    employee_pis = fields.Char("Pis", readonly=True)
    manual = fields.Boolean("Ponto Manual")
    remoteness_point = fields.Boolean()
    remoteness_description = fields.Char()

    def name_get(self):
        return [(rec.id, rec.punch_datetime.strftime("%H:%M") if rec.remoteness_point == False else rec.remoteness_description) for rec in self]

    @api.onchange('employee_id')
    def pis_fill(self):
        self.employee_pis = self.employee_id.employee_pis
        self.manual = True

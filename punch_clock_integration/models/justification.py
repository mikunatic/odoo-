from odoo import fields, models, api
import datetime


class Justification(models.Model):
    _name = 'justification'

    employee_id = fields.Many2one('hr.employee', required=True, string="Funcionário")
    remoteness_id = fields.Many2one('remoteness', required=True, string="Motivo do Afastamento")
    duration = fields.Char(related="remoteness_id.duration", string="Duração")
    first_day = fields.Date("Dia inicial", required=True)
    last_day = fields.Date("Dia final", required=True)
    holidays_ids = fields.Many2many(comodel_name='hr.employee', inverse_name='employee_id',
                                    string="Funcionários que vão folgar no feriado")
    holiday_id = fields.Many2one('justification.holidays', string='Feriado')
    remuneration = fields.Boolean(related='remoteness_id.remuneration', string='Remuneração')
    manual = fields.Boolean()

    @api.onchange('holiday_id')
    def remover_demitidos(self):
        return {'domain': {
            'holidays_ids': [('id', 'not in', self.env['hr.employee'].search([('employee_pis', 'ilike', 'd')]).ids)]}}
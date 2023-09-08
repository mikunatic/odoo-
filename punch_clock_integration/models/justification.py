from odoo import fields, models, api
import datetime


class Justification(models.Model):
    _name = 'justification'

    employee_id = fields.Many2one('hr.employee', required=True, string="Funcionário")
    remoteness_id = fields.Many2one('remoteness', required=True, string="Motivo do Afastamento")
    duration = fields.Char(related="remoteness_id.duration", string="Duração")
    first_day = fields.Date("Dia inicial", required=True)
    last_day = fields.Date("Dia final", required=True)

    # @api.model
    # def create(self, vals_list):
        #iterar no range de dias, e criar UM ponto por dia com o nome da hipótese
        #e fazer alguma forma para diferenciar essa justificativa do ponto normal

        # days_range = (datetime.datetime.strptime(vals_list['last_day'], "%Y-%m-%d")).date() - (datetime.datetime.strptime(vals_list['first_day'], "%Y-%m-%d")).date()
        # days_range = days_range.days + 1
        # i = (datetime.datetime.strptime(vals_list['first_day'], "%Y-%m-%d"))
        # for day in range(days_range):
        #     vals = {
        #         'employee_id':vals_list['employee_id'],
        #         'punch_datetime': i,
        #         'employee_pis': self.env['hr.employee'].browse(vals_list['employee_id']).employee_pis,
        #         'remoteness_point': True,
        #         'remoteness_description': self.env['remoteness'].browse(vals_list['remoteness_id']).hypothesis,
        #     }
        #     i += datetime.timedelta(days=1)
        #     self.env['punch.clock'].create(vals)
        # return super(Justification, self).create(vals_list)
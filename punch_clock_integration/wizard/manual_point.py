from odoo import fields, models


class ManualPoint(models.TransientModel):
    _name = 'manual.point'

    manage_employee_time_id = fields.Integer()
    date = fields.Date()
    hour = fields.Char("Horário do Ponto")
    employee_id = fields.Many2one('hr.employee')

    def confirm(self):
        #Concatena os campos de data e hora respectivamente e os transforma num datetime
        datetime_str = "{} {}".format(self.date, self.hour)
        datetime_field = fields.Datetime.from_string(datetime_str)

        #Criação do ponto manual
        vals_list = {
            'employee_id': self.employee_id.id,
            'punch_datetime': datetime_field,
            'manual': True,
            'employee_pis': self.employee_id.employee_pis,
        }
        new_punch = self.env['punch.clock'].create(vals_list)

        #Pesquisa da linha de onde o botão foi clicado para adicionar o ponto nela
        punch_time_id = self.env['punch.time'].browse(self.env.context.get("active_id"))
        punch_time_id.write({'punch_clock_ids': [[4, new_punch.id, False]]})

        #Retorno para a tela de pesquisa
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pesquisa de Ponto',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manage.employee.time',
            'res_id': self.manage_employee_time_id,
            'views': [[self.env.ref("punch_clock_integration.manage_employee_time_form").id, 'form']],
            'target': 'new'
        }
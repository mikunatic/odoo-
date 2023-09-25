from odoo import fields, models


class AddJustification(models.TransientModel):
    _name = 'add.justification'

    employee_id = fields.Many2one('hr.employee', required=True, string="Funcionário", readonly=1)
    remoteness_id = fields.Many2one('remoteness', required=True, string="Motivo do Afastamento")
    duration = fields.Char(related="remoteness_id.duration", string="Duração")
    first_day = fields.Date("Dia inicial", required=True)
    last_day = fields.Date("Dia final", required=True)
    remuneration = fields.Boolean(related='remoteness_id.remuneration', string='Remuneração')
    manage_employee_time_id = fields.Integer()

    def confirm(self):
        #vals do create da justificativa
        vals_list = {
            'employee_id': self.employee_id.id,
            'remoteness_id': self.remoteness_id.id,
            'first_day': self.first_day,
            'last_day': self.last_day,
            'manual': True,
        }
        #e linkar com o ponto também de alguma forma
        new_justification = self.env['justification'].create(vals_list)

        #pesquisar punch time dentro do range de dias
        punch_time_ids = self.env['punch.time'].search([('manage_employee_time_id','=',self.manage_employee_time_id),
                                                       ('date','<=',self.first_day),('date','>=',self.last_day)])

        #fazer for por cada id e adicionar (n ta funcionando)
        for punch in punch_time_ids:
            punch.write({'justification_id': new_justification.id})
        # punch_time_ids.write({'justification_id': new_justification.id})

        manage_employee_time_id = self.env['manage.employee.time'].browse(self.manage_employee_time_id)
        manage_employee_time_id.write({'attrs_bool':True})
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
from odoo import fields, models


class ManualPoint(models.TransientModel):
    _name = 'manual.point'

    manage_employee_time_id = fields.Many2one('manage.employee.time')
    employees_by_interval_id = fields.Many2one('employees.by.interval')
    date = fields.Date()
    hour = fields.Char("Horário do Ponto")
    employee_id = fields.Many2one('hr.employee')

    def confirm(self):
        #Pesquisa para pegar o dia do objeto "pai" de apontamento do ponto do funcionário
        punch_clock_id = self.env['punch.clock'].search(
            [('punch_date','=',self.date),('employee_id','=',self.employee_id.id)])

        #Cálculo em segundos do horário do ponto manual
        hour, minute = map(int, self.hour.split(':'))
        seconds = hour * 3600 + minute * 60

        #Criação do ponto manual
        vals_list = {
            'time_punch': self.hour,
            'status': 'manual',
            'day_id': punch_clock_id.id,
            'seconds': seconds,
        }
        new_punch = self.env['punch.clock.time'].create(vals_list)

        #Pesquisa da linha de onde o botão foi clicado para adicionar o ponto nela
        punch_time_id = self.env['punch.time'].browse(self.env.context.get("active_id"))
        punch_time_id.write({'punch_time': [[4, new_punch.id, False]]})

        #Retorno para a tela de pesquisa
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pesquisa de Ponto',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manage.employee.time' if punch_time_id.manage_employee_time_id else 'employees.by.interval',
            'res_id': self.manage_employee_time_id.id if punch_time_id.manage_employee_time_id else punch_time_id.employees_by_interval_id.id,
            'views': [[self.env.ref("punch_clock.manage_employee_time_form").id, 'form']] if punch_time_id.manage_employee_time_id else [[self.env.ref("punch_clock.employees_by_interval_form").id, 'form']],
            'target': 'new'
        }
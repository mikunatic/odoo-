from odoo import models, fields


class CreateJustification(models.TransientModel):
    _name = 'create.justification'

    reason = fields.Many2one('remoteness', string="Motivo do Afastamento")

    def create_justification(self):
        active_model = self.env.context.get("active_model")
        vals = {
            'reason': self.reason.id,
            'employee_remoteness_ids': [self._context.get('employee_id')],
            'initial_date': self._context.get('initial_date'),
            'final_date': self._context.get('final_date'),
        }
        self.env['employee.remoteness'].create(vals)
        self.env['punch.time'].browse(self._context.get('child_form')).write({'justification': self.reason.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Justificativa manual',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'manage.employee.time' if active_model == 'manage.employee.time' else 'employees.by.interval',
            'res_id': self._context.get("parent_form"),
            'views': [[self.env.ref("punch_clock.manage_employee_time_form").id, 'form']] if active_model == 'manage.employee.time' else [[self.env.ref("punch_clock.employees_by_interval_form").id, 'form']],
            'target': 'new',
            'context': self._context.copy(),
        }
from odoo import models, fields


class WizardCreatePunchTime(models.TransientModel):
    _name = 'wizard.create.punch.time'

    punch_time = fields.Char(default="00:00", string="Horário da Batida")
    day_id = fields.Many2one('punch.clock')

    def create_punch_time(self):
        # Cálculo em segundos do horário do ponto manual
        hour, minute = map(int, self.punch_time.split(':'))
        seconds = hour * 3600 + minute * 60

        vals = {
            'time_punch': self.punch_time,
            'day_id': self.day_id.id,
            'status': 'manual',
            'seconds': seconds,
        }
        self.env['punch.clock.time'].create(vals)
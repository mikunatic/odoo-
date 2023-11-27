from odoo import fields, models, api


class PunchDisregard(models.TransientModel):
    _name = 'punch.disregard'

    punch_clock_time_ids = fields.Many2many('punch.clock.time', string="Batidas")
    punch_clock_time_id = fields.Many2one('punch.clock.time', string="Ponto")

    @api.onchange('punch_clock_time_ids')
    def unmark_punch(self):
        for punch in self.punch_clock_time_ids:
            if punch.id.origin == self.punch_clock_time_id.id:
                if punch.choose_punch == True:
                    punch.choose_punch = False
                else:
                    self.punch_clock_time_ids = False
        for punch in self.punch_clock_time_ids:
            if punch.choose_punch == True:
                self.punch_clock_time_id = punch.id

    def disregard_punch(self):
        punch_id = self.punch_clock_time_ids.filtered(lambda punch: punch.choose_punch == True)
        punch_id.write({'status':'disregarded'})
        self.punch_clock_time_ids.write({'choose_punch':False})
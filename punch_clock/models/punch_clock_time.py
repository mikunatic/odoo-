from odoo import models, fields


class PunchClockTime(models.Model):
    _name = 'punch.clock.time'
    _description = 'Módulo de horários dos apontamentos do funcionário'
    _rec_name = 'time_punch'
    _order = 'seconds'

    day_id = fields.Many2one('punch.clock')
    time_punch = fields.Char()
    status = fields.Selection([('manual','Manual'),('valid','Válido'),('disregarded','Desconsiderado')])
    color = fields.Integer(compute="_compute_color")
    seconds = fields.Integer()

    def _compute_color(self):
        for rec in self:
            if rec.status == 'manual':
                rec.color = 1
            elif rec.status == 'disregarded':
                rec.color = 9
            else:
                rec.color = 7



    # 12 = branco
    # 11 = roxo
    # 10 = verde
    # 9 = vermelho
    # 8 = azul escuro (quase cinza)
    # 7 = azul
    # 6 = coral
    # 5 = roxo escuro
    # 4 = azul claro
    # 3 = amarelo
    # 2 = laranja claro
    # 1 = amarelo alaranjado
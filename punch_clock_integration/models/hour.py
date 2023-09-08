from odoo import fields, models
from datetime import timedelta


class Hour(models.Model):
    _name = 'hour'
    _rec_name = 'time'

    time = fields.Char()

    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         a = rec.first_hour - timedelta(hours=3)
    #         b = a.strftime('%H:%M:%S')
    #         d = rec.last_hour - timedelta(hours=3)
    #         e = d.strftime('%H:%M:%S')
    #         name = b + " Horário de entrada / " + e + " Horário de entrada"
    #         result.append((rec.id, name))
    #         return result
from odoo import fields, models


class Remoteness(models.Model):
    _name = 'remoteness'
    _rec_name = 'hypothesis'

    hypothesis = fields.Char("Hipótese")
    duration = fields.Char("Duração")
    foundation = fields.Char("Fundamento")


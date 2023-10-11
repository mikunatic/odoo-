from odoo import fields, models


class Syndicate(models.Model):
    _name = 'syndicate'

    name = fields.Char()

    events_syndicate = fields.One2many('events.syndicate', 'syndicate_id', string="Eventos por Sindicato")


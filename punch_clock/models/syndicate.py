from odoo import fields, models


class Syndicate(models.Model):
    _name = 'syndicate'

    name = fields.Char()

    event_ids = fields.Many2many('event', string="Eventos")


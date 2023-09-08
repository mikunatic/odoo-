from odoo import fields, models


class EventsSyndicate(models.Model):
    _name = 'events.syndicate'
    _rec_name = 'event_id'

    value = fields.Integer("Valor")

    syndicate_id = fields.Many2one('syndicate', string="Sindicato")
    event_id = fields.Many2one('event', string="Evento")
from odoo import fields, models


class EventsSyndicate(models.Model):
    _name = 'events.syndicate'

    value = fields.Integer(string="prioridade")

    syndicate_id = fields.Many2one('syndicate', string="Sindicato")
    event_id = fields.Many2one('event', string="Evento")
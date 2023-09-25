from odoo import fields, models


class GeneralConfiguration(models.Model):
    _name = 'general.configuration'

    nighttime_supplement = fields.Integer("Adicional Noturno (%)")
    intraday = fields.Integer("Intrajornada (minutos)")
    interjouney = fields.Integer("Interjornada (horas)")
    arrears_tolerance = fields.Integer("Tolerância de atraso (minutos)")
    virtual_time_validity = fields.Integer("Validade das Horas Virtuais (dias)")
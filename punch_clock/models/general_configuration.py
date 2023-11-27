from odoo import api, fields, models


class ConfigGeral(models.Model):
    _name = 'general.configuration'

    additional_night = fields.Integer(string="Adicional noturno (%)")
    interjourney = fields.Integer(string="Interjornada (horas)")
    intraday = fields.Integer(string="Intrajornada (minutos)")
    arrears_tolerance = fields.Integer(string="Tolerância atraso (minutos)")
    employee_ids = fields.One2many('hr.employee','general_configuration_id')
    virtual_time_validity = fields.Integer("Validade das Horas Virtuais (dias)")
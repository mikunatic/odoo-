from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Rota do Cliente
    route_id = fields.Many2one(
        comodel_name="routes",
        string="Rota"
    )
    # Código HITEC Vinculado
    cod_hitec = fields.Integer(
        string="Código HITEC"
    )
    # Nome Fantasia
    name_fantasy = fields.Char(
        string="Nome Fantasia"
    )

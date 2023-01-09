from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    # Chave Estrangeira da Tabel da tabela fipe no valor de atributo
    fipe_id = fields.Many2one(
        "fipe",
        string="Fipe"
    )
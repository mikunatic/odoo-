from odoo import models, fields, api
from odoo.exceptions import UserError


class Pachave(models.Model):
    _name = 'pachave'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Palavra Chave"
    _rec_name = 'name'

    name = fields.Char(
        'Nome',
        required=True,
        tracking=True
    )
    fipe_ids = fields.Many2many(
        'fipe',
        string='Fipe',
        relation='pachave_fipe_rel'
    )
    value_attr = fields.Many2one(
        "product.attribute.value",
        string="Modelo"
    )

    @api.model
    def create(self, vals_list):
        # Verifica o nome que vai ser salvo
        name_pachave = vals_list["name"]

        # Identifica se o nome já está cadastrado.
        pachave = self.env['pachave'].search([("name", "=", name_pachave)])
        if pachave:
            raise UserError("Nome já cadastrado !!!!")

        # Verifica se já esta criado o model chamado MODELO
        attribute = self.env['product.attribute'].search([("name", "=", "MODELO")], limit=1)
        if attribute.id is False:
            attribute = self.env['product.attribute'].create(
                {"name": "MODELO",
                 "create_variant": "no_variant",
                 "display_type": "radio"}
            )

        # Realiza uma busca para ver se o item já esta cadastrado
        value_attr_exist = self.env['product.attribute.value'].search([("name", "=", name_pachave)])
        if value_attr_exist.id is False:
            value_attr_exist = self.env['product.attribute.value'].create(
                {"name": name_pachave,
                 "attribute_id": attribute.id,
                 "is_custom": False}
            )
            vals_list["value_attr"] = value_attr_exist.id

        return super(Pachave, self).create(vals_list)

    @api.model
    def write(self, id, vals):
        # Identifica se está sendo atualizado o nome da palavra chave
        if "name" in vals:
            pachave = self.env['pachave'].search([("name", "=", vals["name"]), ("id", "!=", id)])
            if pachave:
                raise UserError("Nome já cadastrado !!!!")
            else:
                # Caso não, ele atualiza o atributo relacioando a essa palavra chave
                pachave = self.env['pachave'].browse(ids=id)
                attr_value = self.env['product.attribute.value'].browse(pachave.value_attr.id)
                attr_value.write({"name": vals["name"]})

        return super(Pachave, self.env['pachave'].browse(id)).write(vals)

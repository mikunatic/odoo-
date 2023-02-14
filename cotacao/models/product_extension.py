from odoo import api, models, fields


class ProductExtension(models.Model):
    _inherit = 'product.product'

    fipe_ano = fields.Integer(related='fipe_ids.ano')
    codigo_fipe = fields.Char(related='fipe_ids.codigo_fipe')
    quantidade_a_levar = fields.Float("Quantidade À Levar")
    concorrente_ids = fields.One2many('cadastro.concorrente', 'product_id', string="Concorrente")
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        name_split = name.split()
        array = []
        for palavra in name_split:
            array.append('|')
            array.append('|')
            array.append('|')
            array.append('|')
            array.append(('name', operator, palavra))
            array.append(('product_template_attribute_value_ids',operator,palavra))
            array.append(('fipe_ids',operator,palavra))
            array.append(('codigo_fipe',operator,palavra))
            array.append(('fipe_ano',operator,palavra))
        if name:
            pesquisa = self.search(array)
            return pesquisa.name_get()
        return self.search([('name', operator, name)]+args, limit=limit).name_get()
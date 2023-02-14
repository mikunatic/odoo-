from odoo import fields, models


class CadastroConcorrente(models.Model):
    _name = 'cadastro.concorrente'

    concorrente = fields.Many2one('res.partner', domain="[('active','=',False),('id','not in',[2,4,5,6])]")
    product_id = fields.Many2one('product.product')
    product_price = fields.Float(related='product_id.standard_price', string="Preço Padrão")
    preco_concorrente = fields.Float('Preço de concorrente')

    # def criar_concorrente(self):
    #     for rec in self:
    #         vals_partner = {
    #             'name': rec.concorrente,
    #             'property_account_receivable_id': 25,
    #             'property_account_payable_id': 98,
    #             'active': False,
    #             'concorrente': True,
    #         }
    #         self.env['res.partner'].create(vals_partner)
    #         search_concorrente = self.env['res.partner'].search([], order="id asc")
    #         vals_concorrente = {
    #             'concorrente': search_concorrente[-1],
    #             'product_id': rec.product_id,
    #             'preco_concorrente': rec.preco_concorrente,
    #         }
    #         self.env['concorrente'].create(vals_concorrente)
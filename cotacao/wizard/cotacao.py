from odoo import fields, models,api


class Cotacao(models.TransientModel):
    _name = 'cotacao'

    partner_id = fields.Many2one('res.partner')
    partner_street = fields.Char(related='partner_id.street', string="Rua")
    partner_zip = fields.Char(related='partner_id.zip', string="Código Postal")
    partner_city = fields.Char(related='partner_id.city', string="Cidade")
    partner_route_id = fields.Many2one(related='partner_id.route_id')
    data_vencimento = fields.Date("Data de Vencimento")
    payment_term_id = fields.Many2one('account.payment.term')

    desejado_id = fields.Many2one('product.product')
    qnt_desejado = fields.Float(related='desejado_id.qty_available', string="Em estoque")

    alternativo_ids = fields.Many2many(related='desejado_id.optional_product_ids')
    alternativo = fields.Many2many(comodel_name='product.product', relation='cotacao_rel', domain="[('product_tmpl_id','in',alternativo_ids)]")


    product_categ = fields.Many2one(related='desejado_id.categ_id')

    acessorio_ids = fields.Many2many(related='desejado_id.accessory_product_ids')
    acessorio = fields.Many2many('product.product', domain="[('id','in',acessorio_ids)]")

#FAZER CONTEXT
    def criar(self):

        pre_venda = {
            'partner_id':self.partner_id.id,
            'partner_invoice_id':self.partner_id.id,
            'partner_shipping_id':self.partner_id.id,
            'validity_date':self.data_vencimento,
            'date_order':self.create_date,
            'pricelist_id':1,
            'payment_term_id':self.payment_term_id.id,

        }
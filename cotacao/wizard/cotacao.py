from odoo import fields, models


class Cotacao(models.TransientModel):
    _name = 'cotacao'

    partner_id = fields.Many2one('res.partner')
    partner_street = fields.Char(related='partner_id.street', string="Rua")
    partner_zip = fields.Char(related='partner_id.zip', string="Código Postal")
    partner_city = fields.Char(related='partner_id.city', string="Cidade")
    data_vencimento = fields.Date("Data de Vencimento")
    payment_term_id = fields.Many2one('account.payment.term')
    product_ids = fields.Many2many('product.product')
    product_categ = fields.Many2one(related='product_ids.categ_id')
    template_ids = fields.Many2many('product.template', domain="[('categ_id','=',product_categ)]")# categ_id

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
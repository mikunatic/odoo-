from odoo import fields, models, api,_
from odoo.exceptions import UserError


class CarregaVariante(models.TransientModel):
    _name = 'carrega.variante'
    close_wizard = False

    partner_id = fields.Many2one('res.partner')
    data_vencimento = fields.Date("Data de Vencimento")
    desejado_id = fields.Many2one('product.product', string="Produto", readonly=True)
    preco_desejado = fields.Float(related='desejado_id.standard_price')
    desejado_tmpl_id = fields.Many2one(related="desejado_id.product_tmpl_id")
    variante = fields.Many2many('product.product', relation="variante_carrega_rel")
    qnt_variante = fields.Float(related='variante.qty_available', string="Quantidade em estoque")
    a_levar = fields.Float("À Levar (Por favor, selecionar quantidade igual ou menor à do estoque)")
    qnt_desejado = fields.Float(related='variante.qty_available')
    id_cotacao = fields.Integer()

    acessorio_ids = fields.Many2many(related='variante.accessory_product_ids')
    acessorio = fields.Many2many('product.product', domain="[('id','in',acessorio_ids),('qty_available','>',0)]", relation="acess_do_var_rel")
    int = fields.Integer("int")
    filtro_alternativo = fields.Integer("filt")

    alternativo_ids = fields.Many2many(related="desejado_id.alternative_product_ids", relation="alternativo_da_variante_rel")
    alternativo = fields.Many2many("product.product", relation="alternativo_variante_rel")
    qnt_alternativo = fields.Float(related='alternativo.qty_available', string="Quantidade em estoque")

    acessorio_alt_ids = fields.Many2many(related='alternativo.accessory_product_ids', relation="acess_domain_alt_rel")
    acessorio_alt = fields.Many2many('product.product', domain="[('id','in',acessorio_alt_ids),('qty_available','>',0)]", relation="acess_do_alter_rel")

    produtos_cotados_invisivel = fields.Many2many('product.product', invisible=True, relation="pcinvcv")


    def concluir(self):
        ctx = dict()
        if self.acessorio:
            for acessorio in self.acessorio:
                acessorio_cotar = {
                    'product_id': acessorio.id,
                    'cotacao_id': self.id_cotacao,
                    'quantidade_a_levar': acessorio.quantidade_a_levar,
                    'pre_pedido': True
                }
                if acessorio.quantidade_a_levar == 0:
                    acessorio.quantidade_a_levar = 0
                elif acessorio.quantidade_a_levar > acessorio.qty_available:
                    raise UserError(_("Impossível cotar quantidade maior que a quantidade em estoque"))
                else:
                    self.env['produtos.cotados'].create(acessorio_cotar)
                    acessorio.quantidade_a_levar = 0
        if self.acessorio_alt:
            for acessorio in self.acessorio_alt:
                acessorio_cotar = {
                    'product_id': acessorio.id,
                    'cotacao_id': self.id_cotacao,
                    'quantidade_a_levar': acessorio.quantidade_a_levar,
                    'pre_pedido': True
                }
                if acessorio.quantidade_a_levar == 0:
                    acessorio.quantidade_a_levar = 0
                elif acessorio.quantidade_a_levar > acessorio.qty_available:
                    raise UserError(_("Impossível cotar quantidade maior que a quantidade em estoque"))
                else:
                    self.env['produtos.cotados'].create(acessorio_cotar)
                    acessorio.quantidade_a_levar = 0
        if self.variante:
            for variante in self.variante:
                variantes = {
                    'product_id': variante.id,
                    'cotacao_id': self.id_cotacao,
                    'quantidade_a_levar': variante.quantidade_a_levar,
                    'pre_pedido': True
                }
                if variante.quantidade_a_levar == 0:
                    variante.quantidade_a_levar = 0
                elif variante.quantidade_a_levar > variante.qty_available:
                    raise UserError(_('Quantidade desejada não pode ser maior que a quantidade em estoque!'))
                else:
                    self.env['produtos.cotados'].create(variantes)
                    variante.quantidade_a_levar = 0
            self.env['cotacao'].browse(self.id_cotacao).write({
                'desejado_id': False,
                'quantidade_a_levar': False
            })
        if self.alternativo:
            for alternativo in self.alternativo:
                alternativos = {
                    'product_id': alternativo.id,
                    'cotacao_id': self.id_cotacao,
                    'quantidade_a_levar': alternativo.quantidade_a_levar,
                    'pre_pedido': True
                }
                if alternativo.quantidade_a_levar == 0:
                    alternativo.quantidade_a_levar = 0
                elif alternativo.quantidade_a_levar > alternativo.qty_available:
                    raise UserError(_('Quantidade desejada não pode ser maior que a quantidade em estoque!'))
                else:
                    self.env['produtos.cotados'].create(alternativos)
                    alternativo.quantidade_a_levar = 0
            self.env['cotacao'].browse(self.id_cotacao).write({
                'desejado_id': False,
                'quantidade_a_levar': False
            })
        return
    @api.onchange('desejado_id')
    def domain_variante(self):
        records = self.env['product.product'].search([('product_tmpl_id', '=', self.desejado_tmpl_id.id), ('id', '!=', self.desejado_id.id), ('qty_available', '>', 0)])
        array = []
        for id in records.ids:
            array.append(id)
        length = len(array)
        if length == 0:
            self.int = 1
        elif length > 0:
            self.int = 2
        self.variante = array
        if self.desejado_id:
            return {"domain": {'variante': [('id', 'in', array)]}}
        else:
            return {'domain': {'variante': []}}
    @api.onchange('desejado_id')
    def domain_alt(self):
        domain = []
        search_alt = self.env['product.product'].search([('id', 'in', self.alternativo_ids.ids), ('qty_available', '>', 0)])
        for id in search_alt.ids:
            domain.append(id)
        length = len(domain)
        if length == 0:
            self.filtro_alternativo = 1
        elif length > 0:
            self.filtro_alternativo = 2
        self.alternativo = domain
        if self.desejado_id:
            return {"domain": {'alternativo': [('id', 'in', domain)]}}
        else:
            return {'domain': {'alternativo': []}}

    @api.onchange('variante')
    def popula_acessorio(self):
        for var in self.variante:
            fv = var[0]
            acessorios_variante = self.env['product.product'].search([('id', 'in', fv.accessory_product_ids.ids), ('qty_available','>',0)])
            self.acessorio = acessorios_variante
    @api.onchange('alternativo')
    def popula_acessorio_alt(self):
        for alt in self.alternativo:
            fa = alt[0]
            acessorios_alternativo = self.env['product.product'].search([('id', 'in', fa.accessory_product_ids.ids), ('qty_available', '>', 0)])
            self.acessorio_alt = acessorios_alternativo
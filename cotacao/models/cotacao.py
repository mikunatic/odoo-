from odoo import fields, models, _, api
from odoo.exceptions import UserError
import re
from datetime import date

class Cotacao(models.Model):
    _name = 'cotacao'

    partner_id = fields.Many2one('res.partner', string="Cliente", required=True)
    partner_aux = fields.Many2one('res.partner', string="Cliente")
    partner_street = fields.Char(related='partner_id.street', string="Rua")
    partner_zip = fields.Char(related='partner_id.zip', string="Código Postal")
    partner_city = fields.Char(related='partner_id.city', string="Cidade")
    partner_route_id = fields.Many2one(related='partner_id.route_id')
    partner_properly_product_pricelist = fields.Many2one(related='partner_id.property_product_pricelist')
    data_vencimento = fields.Date("Data de Vencimento", default=fields.Date.today)
    data_emissao = fields.Datetime("Data de Emissão", default=fields.Datetime.now, readonly=True)

    cot_ant = fields.Many2many(comodel_name='cotacao', relation='cotacao_partner_anterior_rel', column1='cot',
                               column2='ant', readonly=True)# cotações anteriores do mesmo cliente

    desejado_id = fields.Many2one('product.product', domain="[('id', 'not in', produtos_cotados_invisivel)]")
    qnt_desejado = fields.Float(related='desejado_id.qty_available', string="Em estoque")
    quantidade_a_levar = fields.Float("Quantidade À Levar")
    prod_cot_id = fields.One2many('produtos.cotados', 'cotacao_id', readonly=True, string="Produtos Cotados")
    int = fields.Integer()
    xml_id = fields.Integer(compute="pega_id")
    produtos_cotados_invisivel = fields.Many2many('product.product', relation="pcinvc")
    expirado = fields.Boolean()

    def carregaproduto(self):
        for rec in self:
            # hoje = date.today()
            # if rec.data_vencimento > hoje:
            #     rec.expirado = False
                if rec.quantidade_a_levar > 0:
                    array = []
                    for produto in rec.produtos_cotados_invisivel.ids:
                        array.append(produto)
                    array.append(rec.desejado_id.id)
                    ctx = dict()
                    ctx.update({
                        'default_partner_id': self.partner_id.id,
                        'default_desejado_id': self.desejado_id.id,
                        'default_produtos_cotados_invisivel': array,
                        'default_quantidade_a_levar': self.quantidade_a_levar
                    })
                    return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'carrega.produto',
                    'views': [[self.env.ref("cotacao.carrega_produto_form_view").id, 'form']],
                    'context': ctx,
                    'target': 'new'
                    }
                elif rec.quantidade_a_levar == 0:
                    raise UserError(_("Impossível cotar produto com quantidade igual à zero! \nSelecione uma quantidade."))
            # else:
            #     rec.expirado = True
            #     raise UserError(_("Cotação Expirada"))
    def cria_pre_pedido(self):
            ctx = dict()
            for rec in self:
                rec.int = 10
                pattern = '\d'
                string = ''
                result = re.findall(pattern, str(rec.id))
                for num in result:
                        string += num
                vals_list = {
                    'cotacao':int(string),
                    'partner_id': self.partner_id.id,
                    'validity_date': self.data_vencimento,
                }
                quote = self.env['sale.order'].create(vals_list)
                for prods in self.prod_cot_id:
                    name = prods.name + ' ' + '(' + prods.product_template_attribute_value_ids.name + ')'
                    if prods.pre_pedido == True:
                        vals_lines = ({
                            'order_line': [(0, 0, {'product_id': prods.product_id.id,
                                                   'product_template_id': prods.product_id.product_tmpl_id,
                                                   'name': name,
                                                   'price_unit': prods.standard_price,
                                                   'product_uom_qty': prods.quantidade_a_levar,
                                                    })]
                        })
                        quote.write(vals_lines)
                return {
                    'type': "ir.actions.act_window",
                    'view_type': "form",
                    'view_mode': "form",
                    'res_id': quote.id,
                    'res_model': "sale.order",
                    'views': [[self.env.ref("sale.view_order_form").id, 'form']],
                    'target': 'current',
                    'context': ctx
                }
    def abre_pre_pedido(self):
        for rec in self:
            ctx = dict()
            pattern = '\d'
            string = ''
            result = re.findall(pattern, str(rec.id))
            for num in result:
                string += num
            pp = self.env['sale.order'].search([('cotacao.id', '=', int(string))], order='id asc')# pesquisar sale order q tem o id da cotacao atual no campo cotacao, depois retornar no domain
            return {
                "type": "ir.actions.act_window",
                "name": _(""),
                "res_model": "sale.order",
                "domain": [("id", "=", pp.id)],
                "view_mode": "tree,form",
                "context": self.env.context
            }
    @api.onchange('desejado_id')
    def domain_produto(self):
        for rec in self:
            produtos_escolhidos = []
            for prod in rec.prod_cot_id:
                produtos_escolhidos.append(prod.product_id)
            if self.partner_id:
                return {"domain": {'desejado_id': [('id', 'not in', produtos_escolhidos)]}}
            else:
                return {'domain': {'desejado_id': []}}
    def pega_id(self):
        for rec in self:
            pattern = '\d+$' # regex q busca qualquer dígito
            var_id = re.findall(pattern, str(rec.id))
            integerfication = int(var_id[0])
            rec.xml_id = integerfication
            cotacoes = self.env['cotacao'].search([])
    @api.onchange('partner_id')
    def cotacoes_anteriores(self):
        for rec in self:
            pattern = '\d+$'
            var_id = re.findall(pattern, str(rec.id))
            integerfication = int(var_id[0])
            rec.partner_aux = rec.partner_id.id
            cotacoes = self.env['cotacao'].search([('id', '!=', integerfication), ('partner_id', '=', rec.partner_aux.id)])
            rec.cot_ant = cotacoes.ids

    @api.onchange('data_vencimento')
    def valida_data(self):
        for rec in self:
            hoje = date.today()
            if rec.data_vencimento < hoje:
                rec.data_vencimento.today()
                raise UserError(_("Não é possível criar cotação com data anterior à atual"))
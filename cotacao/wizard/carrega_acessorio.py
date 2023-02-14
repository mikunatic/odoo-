from odoo import fields, models,_
from odoo.exceptions import UserError


class CarregaAcessorio(models.TransientModel):
    _name = 'carrega.acessorio'
    close_wizard = False

    partner_id = fields.Many2one('res.partner')
    desejado_id = fields.Many2one('product.product', string="Produto", readonly=True)
    preco_desejado_id = fields.Float(related='desejado_id.standard_price', string="Preço do Produto", readonly=True)
    acessorio_ids = fields.Many2many(related='desejado_id.accessory_product_ids')
    acessorio = fields.Many2many('product.product', domain="[('id','in',acessorio_ids),('qty_available','>',0)]")
    id_cotacao = fields.Integer()
    produtos_cotados_invisivel = fields.Many2many('product.product', invisible=True, relation="pcinvca")

    concorrente = fields.One2many(related="desejado_id.concorrente_ids", readonly=False, string="Concorrente")
    concorrente_nome = fields.Many2one('res.partner',string="Concorrente")
    concorrente_valor = fields.Float()
    def cotar(self):
        for acess in self.acessorio:
            acessorio_cotar = ({
                'product_id': acess.id,
                'cotacao_id': self.id_cotacao,
                'quantidade_a_levar': acess.quantidade_a_levar,
                'pre_pedido': True
            })
            if acess.quantidade_a_levar <= acess.qty_available:
                self.env['produtos.cotados'].create(acessorio_cotar)
            elif acess.quantidade_a_levar > acess.qty_available:
                raise UserError(_("Impossível cotar quantidade maior que a quantidade em estoque"))
            acess.quantidade_a_levar = 0
        array = []
        for produto in self.produtos_cotados_invisivel.ids:
            array.append(produto)
        for produto in self.acessorio.ids:
            array.append(produto)
        array.append(self.desejado_id.id)
        self.env['cotacao'].browse(self.id_cotacao).write({
            'desejado_id': False,
            'quantidade_a_levar': False,
            'produtos_cotados_invisivel': array
        })
        return

    def cadastra_concorrente(self):
        action = self.env['cadastro.concorrente'].cadastro_concorrente_action()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cadastro.concorrente',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [(action['id'], 'form')],
            'view_id': action['id'],
        }





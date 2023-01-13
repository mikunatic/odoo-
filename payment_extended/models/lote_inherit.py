from odoo import fields, models,api


class LoteInherit(models.Model):
    _inherit = 'lote.cheque'

    cheque_ids = fields.Many2many('cadastro.cheque', domain="[('pagamentos','=',False)]")
    currency_id = fields.Many2one('res.currency', default=6)
    valor_total = fields.Monetary(currency_field='currency_id', compute="calculartotal")
    pagamento_ids = fields.One2many('account.payment', 'lote_id')

    @api.depends("cheque_ids")
    def calculartotal(self):
        valor = 0
        for lote in self:
            for cheque in lote.cheque_ids:
                valor += cheque.valor
            lote.valor_total = valor

    @api.onchange("cheque_ids","pagamento_ids")
    def update_cheque(self):
        pagamentos = [] # cria uma array
        cheques = []
        for rec in self: # caminha pelos records
            pagamentos = rec.pagamento_ids.ids # cria variável pra armazenar todos os pagamentos que o lote fez
            cheques = self.env['cadastro.cheque'].search(["id","in",rec.cheque_ids.ids]) # cria variável que procura e armazena os cheques
        for cheque in cheques:
            cheque.update({'pagamentos': pagamentos})



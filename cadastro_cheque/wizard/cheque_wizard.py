from odoo import models,_


class ChequeWizard(models.TransientModel):
    _name = "cheque.wiz"

    def post(self):
        pagamento = self.env['account.payment'].search([], order="id asc") # pesquisa os pagamento por ordem de id crescente
        description = self.env['cadastro.cheque'].search([], order="id asc") # armazena na variavel os meus pagamentos criados pesquisados por ordem crescente de id
        pagamento[-1].action_post() # posta o pagamento mais recente
        pagamento[-2].action_post() # posta o pagamento mais recente

        desc = description[-1].descricao # adiciona a descrição personalizada no gerproc criado com o valor e a data do pagamento
        vals_ger_proc = {'status': 'aberto',
                     'private_message': 'public',
                     'department_id': 4,  # required
                     'user_requested_id': 1,
                     'users_views_ids': [[6, False, []]],
                     'department_views_ids': [[6, False, [1, 2, 3]]],
                     'category_parent_request_id': 4,  # required
                     'category_child_request': 5,  # required
                     'boolean_client': False,
                     'request_client_ids': [[6, False, []]],
                     'description_problem': desc,  # required
                     'my_requests': [[6, False, []]],
                     'message_follower_ids': [],
                     'activity_ids': [],
                     'message_ids': [],
                    } # lista de valores para criação do gerproc

        self.env['project_request'].create(vals_ger_proc) # cria um gerproc com os dados passados na lista acima
        last_gp = self.env['project_request'].search([], order="id asc") # pesquisa os gerprocs e ordena por id ascendente
        gpr = last_gp[-1] # armazena na variavel gpr o último gerproc criado
        pagamento[-1].update({'gerproc':gpr.id}) # atualiza o campo gerproc, presente no account.payment, com o id do ultimo gerproc, no pagamento e recebimento
        pagamento[-2].update({'gerproc':gpr.id})
        description[-1].update({'gerproc_id':gpr.id})

        # Retorna a tree com apenas o gerproc criado
        # return {
        #     "type": "ir.actions.act_window",
        #     "name":_("Project Request"),
        #     "res_model":"project_request",
        #     "domain":[("id", "=", gpr.id)],
        #     "view_mode":"tree,form",
        #     "context": self.env.context
        # }
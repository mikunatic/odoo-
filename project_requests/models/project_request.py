import logging

logger = logging.getLogger(__name__)
from odoo import models, api, fields
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import pandas as pd


class ProjectRequest(models.Model):
    _name = 'project_request'
    _order = 'status'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "protocol"

    request_client_ids = fields.Many2many("res.partner",
                                          string="Cliente da Requisição")

    # Usuário que realizou a abertura da requisição
    user_id = fields.Many2one(
        "res.users",
        string="Usuário de Abertura",
        readonly=True,
        default=lambda self: self.env.uid
    )
    # A lista manny2many para poder referenciar algum chamado anterior
    my_requests = fields.Many2many(
        "project_request",
        'project_requests_depends_rel',
        "id",
        string='Minhas Requisições'
        # domain=[('create_uid', '=', 'chamado_servico.create_uid')]
    )
    # Descrição do problema para abertura da requisição
    description_problem = fields.Text(
        "Descrição",
        required=True,
        tracking=True
    )
    # Categoria do assunto da requisição
    category_parent_request_id = fields.Many2one(
        "category_request",
        string="Categoria",
        required=True
    )
    boolean_client = fields.Boolean(
        string="Showing a client",
        invisible=True,
        default=False
    )
    # Assunto da requisição
    category_child_request = fields.Many2one(
        "category_request",
        string="Assunto da Requisição",
        required=True
    )

    @api.onchange("category_child_request")
    def category_child_request_on_change(self):
        for request in self:
            if request.category_child_request.has_client is True:
                self.boolean_client = True
            else:
                self.boolean_client = False

    # Função para exibir os assuntos especificos de uma categoria
    @api.onchange("category_parent_request_id")
    def category_parent_request_on_change(self):
        for request in self:
            if request.category_parent_request_id.id != request.category_child_request.parent_id.id:
                request.category_child_request = self.env["category_request"]
            if int(request.user_id.department_id.id).__eq__(int(request.department_id.id)):
                internal_response = [True, False]
            else:
                internal_response = [False]
            return {'domain': {'category_child_request': [('type', '=', 'child'),
                                                          ('status', '=', 'Habilitado'),
                                                          ('parent_id', '=', request.category_parent_request_id.ids),
                                                          ('internal_request', 'in', internal_response)]}}

    # Campo para perguntar se a requisição é "publica" ou privada
    private_message = fields.Selection(
        [
            ("public", "Público"),
            ("private", "Privado")
        ],
        default="public",
        required=True
    )

    # On change para verificar qualquer alteração do tipo de privacidade do chamado.
    @api.onchange("private_message")
    def one_change_private_message(self):
        for rec in self:
            department_id = 0
            if rec.private_message.__eq__("private"):
                if rec.department_id.id > 0:
                    department_id = rec.department_id.id
            return {'domain': {'user_requested_id': [('department_id', '=', department_id)]}}

    # Usuario solicitado para responder a mensagem caso ela sejá privada
    user_requested_id = fields.Many2one(
        "res.users",
        string="Usuário Solicitado"
    )
    # Resposta ao chamado aberto
    response_problem = fields.Text(
        "Resposta / Solução",
        tracking=True
    )
    # Status da requisição para dar continuidade
    status = fields.Selection([
        ('aberto', 'Aberto'),
        ('andamento', 'Em Andamento'),
        ('aguardando_resposta', 'Aguardando Resposta'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado')
    ], 'Status', default='aberto', tracking=True)
    # Data de Abertura da Requisição
    opening_date = fields.Date(
        'Data do Abertura da Requisição',
        default=datetime.today(),
        readonly=True
    )
    # Data da Ultima Atualização de status feita nela
    update_date = fields.Date(
        'Data da última atualização',
        default=datetime.today(),
        readonly=True
    )
    # Data de vencimento para resposta do chamado
    due_date = fields.Date(
        "Data de vencimento da Requisição"
    )
    # Protocolo para usuario solicitante poder acompanhar os chamados
    protocol = fields.Char(
        string='Protocolo',
        readonly=True,
        compute='create',
        store=True
    )
    # Departamento Solicitante
    department_id = fields.Many2one(
        "hr.department",
        "Departamento",
        required=True
    )
    # Usuarios que podem acessar a requisição
    users_views_ids = fields.Many2many(
        "res.users",
        string="Usuários com Acesso a requisição"
    )
    # Departamentos que podem acessar a requisição
    department_views_ids = fields.Many2many(
        "hr.department",
        string="Departamentos com Acesso a requisição"
    )
    # Verificar se o usuario é o responsavel para responder
    is_required = fields.Boolean(
        "É o solicitado",
        default=True,
        compute="compute_is_required"
    )

    def compute_is_required(self):
        for rec in self:
            if rec.private_message.__eq__("private"):
                if rec.env.user.id.__eq__(rec.user_requested_id.id):
                    rec.is_required = True
                else:
                    rec.is_required = False
            else:
                if rec.env.user.department_id.id.__eq__(rec.department_id.id):
                    rec.is_required = True
                else:
                    rec.is_required = False

    user_create_id = fields.Boolean(
        string='É o usuario que criou requisição',
        default=True,
        compute='get_current_uid'
    )

    def get_current_uid(self):
        for rec in self:
            if rec.env.user.id == rec.user_id.id:
                rec.user_create_id = True
            else:
                rec.user_create_id = False

    # Função para exibir os assuntos especificos de uma categoria
    @api.onchange("department_id")
    def departament_on_change(self):
        for request in self:
            if request.department_id.id != request.category_parent_request_id.id:
                request.category_parent_request_id = self.env["category_request"]
            if request.department_id.id != request.user_requested_id.department_id.id:
                request.user_requested_id = self.env['res.users']
            if int(request.user_id.department_id.id).__eq__(int(request.department_id.id)):
                internal_response = [True, False]
            else:
                internal_response = [False]
            return {'domain': {'category_parent_request_id': [('type', '=', 'parent'),
                                                              ('department_id', '=', request.department_id.ids),
                                                              ('status', '=', 'Habilitado'),
                                                              ('internal_request', 'in', internal_response)],
                               'user_requested_id': [('department_id', '=', request.department_id.id)]}}

    # Função para retornar um nome para o model quando ele é chamado
    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s / %s " % (record.create_uid.name, record.protocol)
            result.append((record.id, rec_name))
        return result

    # Botão para atualizar o status da requisição para em andamento
    def next_in_progress(self):
        self.alter_status('andamento')
        self.write({
            "update_date": fields.datetime.today()
        })

    # Botão para atualizar o status da requisição para em andamento
    def next_reverse(self):
        self.alter_status('andamento')
        self.write({
            "update_date": fields.datetime.today()
        })

    # Botão para atualizar o status da requisição para Finalizado
    def next_waiting_answer(self):
        self.alter_status('aguardando_resposta')
        self.write({
            "update_date": fields.datetime.today()
        })

    # Botão para o usuario poder responder a requisição
    def response_progress(self):
        ctx = dict()
        ctx.update({
            'default_model': 'response_request',
            'default_project_request_id': self.id
        })
        wizard_action = {
            "type": "ir.actions.act_window",
            "res_model": "response_request",
            "name": "Responder a Pendência",
            "views": [
                [
                    self.env.ref("project_requests.view_response_request_form").id,
                    "form",
                ]
            ],
            "context": ctx,
            "view_mode": "form",
            "target": "new",
        }
        return wizard_action

    # Botão para atualizar o status da requisição para Finalizado
    def next_finished(self):
        self.alter_status('finalizado')
        self.write({
            "update_date": fields.datetime.today()
        })

    # Botão para atualizar o status da requisição para Cancelado
    def next_canceled(self):
        self.alter_status('cancelado')
        self.write({
            "update_date": fields.datetime.today()
        })

    @api.model
    def create(self, vals):
        # Formatando a data para iniciar a criação do protocolo
        format_date = str(fields.Date.today()).replace("-", "")
        # Recuperando o ultimo ID inserido no banco de dados
        try:
            last_id = self.search([], order='id desc')[0].id + 1
        except:
            last_id = 1
        # Quantidade de 0 para a geração do protocolo
        zeros = "0000"
        # Formatando e adicionado os 0 para deixar 5 digitos
        initial_protocol = zeros[0:(4 - (len(str(last_id)) - 1))] + str(last_id)
        # Concatenando a data mais o protocolo
        format_date += initial_protocol
        # Atribui os valores das propriedades do model
        vals["update_date"] = fields.Date.today()
        vals["opening_date"] = fields.Date.today()
        vals["protocol"] = format_date

        # if vals['private_message'].__eq__("private"):
        #     user_id = self.env["res.users"].browse([vals["user_requested_id"]])
        #     user_id.notify_info(
        #         message='Nova Requisição gerada do usuário %s, protocolo %s' % (self.env.user.name, format_date))
        # else:
        #     for user_id in self.env["res.users"].search([("department_id", "=", vals["department_id"])]):
        #         user_id.notify_info(
        #             message='Nova Requisição gerada do usuário %s, protocolo %s' % (self.env.user.name, format_date))

        # Realiza a validação da data de vencimento
        vals["due_date"] = self.validate_answer(category_id=vals['category_child_request'])
        # Retorna e salva a requisição
        return super(ProjectRequest, self).create(vals)

    # Compute para retornar a data maxima de atendimento do chamado
    def validate_answer(self, category_id, opening_date=fields.Date.today()):
        # Atribui a quantidade de dias configuradas nas categorias
        count = self.env["category_request"].browse([category_id]).due_date
        # Atribui o dia de abertura da requisição
        if count > 0:
            due_date = opening_date + timedelta(days=count)
            due_date = opening_date + pd.DateOffset(days=count)
            if due_date.weekday() == 5:
                due_date += pd.DateOffset(days=2)
            elif due_date.weekday() == 6:
                due_date += pd.DateOffset(days=1)
            return due_date
        else:
            due_date = opening_date
            if due_date.weekday() == 5:
                due_date += pd.DateOffset(days=2)
            return due_date

    def write(self, vals):
        if 'category_child_request' in vals:
            vals["due_date"] = self.validate_answer(category_id=vals['category_child_request'])
        return super(ProjectRequest, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.status != "aberto":
                raise UserError(
                    "Não é possivel escluir a requisição do protocolo " + rec.protocol + ", pois não está mais no status "
                                                                                      "em aberto")
        return super(ProjectRequest, self).unlink()

    # Validar as possiveis mudanças de status
    @api.model
    def validate_alter_status(self, old_state, new_state):
        allowed = [
            ('aberto', 'andamento'),
            ('andamento', 'finalizado'),
            ('andamento', 'cancelado'),
            ('aguardando_resposta', 'andamento'),
            ('aguardando_resposta', 'finalizado'),
            ('aguardando_resposta', 'cancelado'),
            ('andamento', 'aguardando_resposta'),
            ('aberto', 'cancelado'),
            ('cancelado', 'andamento'),
            ('finalizado', 'andamento'),
        ]
        return (old_state, new_state) in allowed

    def alter_status(self, new_state):
        for request in self:
            if request.validate_alter_status(request.status, new_state):
                request.status = new_state
            else:
                msg = 'Status de %s para %s não é permitido.' % (request.status, new_state)
                raise UserError(msg)

from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

from odoo import models, api, fields


class Recurring(models.Model):
    _name = "project_request.recurring"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    seg = fields.Boolean(string='Seg')
    ter = fields.Boolean(string='Ter')
    qua = fields.Boolean(string='Qua')
    qui = fields.Boolean(string='Qui')
    sex = fields.Boolean(string='Sex')
    sab = fields.Boolean(string='Sab')
    dom = fields.Boolean(string='Dom')

    # next_recurrence_date = fields.Date()
    # Usuário que realizou a abertura da requisição
    user_id = fields.Many2one(
        "res.users",
        string="Usuário de Abertura",
        readonly=True,
        default=lambda self: self.env.uid,
        tracking=True
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
        required=True,
        tracking=True
    )

    repeat_month = fields.Selection([
        ('1', 'Janeiro'),
        ('2', 'Fevereiro'),
        ('3', 'Março'),
        ('4', 'Abril'),
        ('5', 'Maio'),
        ('6', 'Junho'),
        ('7', 'Julho'),
        ('8', 'Agosto'),
        ('9', 'Setembro'),
        ('10', 'Outubro'),
        ('11', 'Novembro'),
        ('12', 'Dezembro'),
    ], string='Mês')

    repeat_day = fields.Selection([
        (str(i), str(i)) for i in range(1, 32)
    ], string="Dia do mês")

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

    boolean_client = fields.Boolean(
        string="Showing a client",
        invisible=True,
        default=False,
        tracking=True
    )
    request_client_ids = fields.Many2many("res.partner", string="Cliente da Requisição")
    # Assunto da requisição
    category_child_request = fields.Many2one(
        "category_request",
        string="Assunto da Requisição",
        required=True,
        tracking=True
    )

    @api.onchange("category_child_request")
    def category_child_request_on_change(self):
        for request in self:
            if request.category_child_request.has_client is True:
                self.boolean_client = True
            else:
                self.boolean_client = False

    # Campo para perguntar se a requisição é "publica" ou privada
    private_message = fields.Selection(
        [
            ("public", "Público"),
            ("private", "Privado")
        ],
        default="public",
        required=True,
        tracking=True
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
        string="Usuário Solicitado",
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
    # Departamento Solicitante
    department_id = fields.Many2one(
        "hr.department",
        "Departamento",
        required=True,
        tracking=True
    )

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

    # Usuarios que podem acessar a requisição
    users_views_ids = fields.Many2many(
        "res.users",
        string="Usuários com Acesso a requisição",
        tracking=True
    )

    # Departamentos que podem acessar a requisição
    department_views_ids = fields.Many2many(
        "hr.department",
        string="Departamentos com Acesso a requisição",
        tracking=True
    )

    # Verificar se o usuario é o responsavel para responder
    is_required = fields.Boolean(
        "É o solicitado",
        default=True,
        tracking=True
    )

    user_create_id = fields.Boolean(
        string='É o usuario que criou requisição',
        default=True,
        tracking=True
    )

    repeat_interval = fields.Integer(
        string="Repetir a Cada",
        default=1,
        tracking=True
    )

    repeat_unit = fields.Selection(
        selection=[
            ("day", "Dias"),
            ("week", "Semanas"),
            ("month", "Meses"),
            ("year", "Anos")
        ],
        tracking=True
    )

    repeat_type = fields.Selection(
        selection=[
            ("forever", "Para Sempre"),
            ("until", "Data Final"),
            ("after", "Número de Repetições")
        ],
        tracking=True,
        string='Tipo de Repetição'
    )

    repeat_until_date = fields.Date(
        string="Data Final",
        tracking=True
    )

    repeat_quantity = fields.Integer(
        string="Quantidade",
        tracking=True
    )

    project_request_ids = fields.Many2many(
        "project_request",
        string="Project Request Gerado",
        tracking=True,
        index=True
    )

    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="recurring_id",
        string="Anexos Vinculados",
        tracking=True
    )

    enabled = fields.Boolean(
        "Status do Agendamento",
        default=True,
        tracking=True
    )

    create_date = fields.Date(
        default=datetime.today()
    )

    @api.onchange("repeat_unit")
    def _clear_week(self):
        if self.repeat_unit == "week":
            self.seg = False
            self.ter = False
            self.qua = False
            self.qui = False
            self.sex = False
            self.sab = False
            self.dom = False
        elif self.repeat_unit == "month":
            self.repeat_day = False
        elif self.repeat_unit == "year":
            self.repeat_day = False
            self.repeat_month = False
        else:
            self.seg = False
            self.ter = False
            self.qua = False
            self.qui = False
            self.sex = False
            self.sab = False
            self.dom = False
            self.repeat_day = False
            self.repeat_month = False

    @api.constrains('repeat_unit', 'seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom')
    def _check_recurrence_days(self):
        for project in self.filtered(lambda p: p.repeat_unit == 'week'):
            if not any([project.seg, project.ter, project.qua, project.qui, project.sex, project.sab, project.dom]):
                raise ValidationError('Coloque pelo menos um dia')

    @api.constrains('repeat_interval')
    def _check_repeat_interval(self):
        if self.filtered(lambda t: t.repeat_interval <= 0):
            raise ValidationError('O intervalo deve ser maior que 0')

    def return_date_today(self,
                          date=datetime.today()):  # função para verificar qual dia da semana o agendamento vai ocorrer
        if self.seg and date.weekday() == 0:
            return True
        if self.ter and date.weekday() == 1:
            return True
        if self.qua and date.weekday() == 2:
            return True
        if self.qui and date.weekday() == 3:
            return True
        if self.sex and date.weekday() == 4:
            return True
        if self.sab and date.weekday() == 5:
            return True
        if self.dom and date.weekday() == 6:
            return True
        else:
            return False

    def return_day(self, vals, date=datetime.today()):
        data = vals['create_date']
        if self.project_request_ids.ids:
            if len(self.project_request_ids) == 1:
                lista = self.project_request_ids[0]
            elif len(self.project_request_ids) == 0:
                if date.day == self.create_date.day:
                    return True
            else:
                lista = self.env["project_request"].search([('id', 'in', self.project_request_ids.ids)], limit=1, order='id desc')
            data_validator_day = lista.opening_date + relativedelta(days=self.repeat_interval)
            if data_validator_day.day == date.day:
                return True
        if date.day == data.day:
            return True
        else:
            return False

    def return_month(self, date=date.today()):
        relative_date = datetime(datetime.today().year, datetime.today().month,
                                 int(self.repeat_day))  # data do agendamento
        if len(self.project_request_ids.ids) > 0:  # verifica se já existe um project request
            data_abertura = self.project_request_ids[
                len(self.project_request_ids.ids) - 1].opening_date  # ultima data de abertura do agendamento
            data_validator = data_abertura + relativedelta(
                months=self.repeat_interval)  # data do próximo agendamento com base nos intervalos de repetição
            if data_validator == date:
                return True
        if len(self.project_request_ids.ids) == 0:
            data_validator_today = relative_date + relativedelta(
                months=self.repeat_interval)  # data do próximo agendamento com base nos intervalos de repetição
            new_date = date + relativedelta(
                months=self.repeat_interval)  # variável que soma a data atual e o intervalo de repetição (mês)
            if data_validator_today == new_date:
                return True
        if relative_date.month == datetime.today().month and relative_date.day == datetime.today().day:
            return True
        return False

    def return_year(self, date=datetime.today()):
        relative_date_years = datetime(datetime.today().year, int(self.repeat_month),
                                       int(self.repeat_day))  # data do agendamento
        if len(self.project_request_ids.ids) > 0:  # verifica se já existe um project request
            data_abertura_years = self.project_request_ids[
                len(self.project_request_ids.ids) - 1].opening_date  # ultima data de abertura do agendamento
            data_validator_years = data_abertura_years + relativedelta(
                years=self.repeat_interval)  # variável que soma a data atual e o intervalo de repetição (ano)
            if data_validator_years != date:
                return False
            else:
                return True
        if len(self.project_request_ids.ids) == 0:
            data_validator_today_years = relative_date_years + relativedelta(
                years=self.repeat_interval)  # data do próximo agendamento com base nos intervalos de repetição
            new_date_years = date + relativedelta(
                years=self.repeat_interval)  # variável que soma a data atual e o intervalo de repetição (ano)
            if data_validator_today_years == new_date_years:
                return True
        if relative_date_years.year == datetime.today().year and relative_date_years.month == datetime.today().month and relative_date_years.day == datetime.today().day:
            return True
        return False

    def auto_generate(self):
        for rec in self.search([("enabled", "=", True)]):
            interval_repeat = rec.repeat_interval
            # Verifica o tipo de Request
            if rec.repeat_type.__eq__("after"):
                if rec.repeat_quantity <= len(rec.project_request_ids.ids):
                    continue
            elif rec.repeat_type.__eq__("until"):
                data = date.today()
                if rec.repeat_until_date < data:
                    continue
                # Verifica se deve lançar um novo project Request
            if rec.repeat_unit.__eq__("day"):
                if not rec.return_day({"create_date": rec.create_date}):
                    continue
            elif rec.repeat_unit.__eq__("week"):  # se o ger proc é semanal!
                if not rec.return_date_today():
                    continue
            elif rec.repeat_unit.__eq__("month"):
                if not rec.return_month():
                    continue
            else:
                if not rec.return_year():
                    continue
            valores = {
                "status": "aberto",
                "user_id": rec.user_id.id,
                "cqd_id": False,
                "user_requested_id": rec.user_requested_id.id if rec.user_requested_id else False,
                "private_message": rec.private_message,
                "department_id": rec.department_id.id,
                "users_views_ids": [[6, False, rec.users_views_ids.ids]],
                "department_views_ids": [[6, False, rec.department_views_ids.ids]],
                "category_parent_request_id": rec.category_parent_request_id.id,
                "category_child_request": rec.category_child_request.id,
                "boolean_client": rec.boolean_client,
                "request_client_ids": [[6, False, rec.request_client_ids.ids]],
                "description_problem": rec.description_problem,
                "my_requests": [[6, False, []]],
                "message_follower_ids": [],
                "activity_ids": [],
                "message_ids": []
            }
            recurring_id = self.create_gerProc(valores)
            rec.write({'project_request_ids': [(4, recurring_id.id)]})
            rec.send_message(recurring_id=recurring_id)

    def send_message(self, recurring_id):
        if recurring_id.private_message.__eq__("public"):
            for user in recurring_id.department_id.member_ids.user_partner_id:
                channel = self.env['mail.channel'].channel_get([user.id])
                channel_id = self.env['mail.channel'].browse(channel["id"])
                channel_id.message_post(
                    body=r'Nova Requisição aberta, protocolo %s' % recurring_id.protocol,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                )
        else:
            channel = self.env['mail.channel'].channel_get([recurring_id.user_requested_id.partner_id.id])
            channel_id = self.env['mail.channel'].browse(channel["id"])
            channel_id.message_post(
                body=r'Nova Requisição aberta, protocolo %s' % recurring_id.protocol,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '%s %s' % ('Recorrência nº ', record.id)))
        return result
    @api.model
    def create(self, vals):
        rtn = super(Recurring, self).create(vals)
        if vals['repeat_unit'].__eq__("day"):
            vals['create_date'] = rtn.create_date
            if self.return_day(vals) == True:
                recurring_id = self.create_gerProc(vals)
                rtn.write({'project_request_ids': [(4, recurring_id.id)]})
                rtn.send_message(recurring_id=recurring_id)
            return rtn
        else:
            return rtn
    def create_gerProc(self, vals):
        vals_list = {
                    "status": "aberto",
                    "user_id": self.env.user.id,
                    "user_requested_id": self.user_requested_id.id if self.user_requested_id else False,
                    "private_message": vals['private_message'],
                    "department_id": vals['department_id'],
                    "users_views_ids": [[6, False, self.users_views_ids.ids]],
                    "department_views_ids": [[6, False, self.department_views_ids.ids]],
                    "category_parent_request_id": vals['category_parent_request_id'],
                    "category_child_request": vals['category_child_request'],
                    "boolean_client": vals['boolean_client'],
                    "request_client_ids": [[6, False, self.request_client_ids.ids]],
                    "description_problem": vals['description_problem'],
                    "my_requests": [[6, False, []]],
                    "message_follower_ids": [],
                    "activity_ids": [],
                    "message_ids": []
                }
        ger_proc = self.env['project_request'].create(vals_list)
        return ger_proc

    def unlink(self):
        if self.enabled:
            raise UserError("Não é possivel realizar a exclusão de um chamado ativo")
        elif self.project_request_ids:
            raise UserError(
                "Não é possivel realizar a exclusão , pois já tem project requests gerados dele.\n Recomendado "
                "Inativar o agendamento.")
        return super(Recurring, self).unlink()

import datetime
from odoo import models, fields, _
import base64
import os


class PunchClockIntegration(models.TransientModel):
    _name = 'punch.clock.integration'

    afd_file = fields.Binary(string="Arquivo AFD", required=True)

    def call_function(self):
        # Chama a função adequada de acordo com o arquivo de ponto
        content = base64.b64decode(self.afd_file)
        content = content.decode('utf-8').split('\r\n')

        # Diferenciação de afd para aplicar a tratativa adequada
        if '00004004330204941' in content[0]:
            # Apaga as linhas que não dizem respeito aos apontamentos
            content.pop(-1)
            content.pop(-1)
            for i in range(48):
                content.remove(content[0])

            # Arquivo de comparação
            punch_file = os.path.dirname(os.path.abspath(__file__)).replace('wizard', 'data') + '/ponto_fabrica.txt'

            self.create_fabrica(content, punch_file)
        elif '00004004330134958' in content[0]:
            # Apaga as linhas que não dizem respeito aos apontamentos
            content.pop(-1)
            content.pop(-1)
            for i in range(22):  # As 22 primeiras linhas dizem respeito ao relogio
                content.remove(content[0])

            # Arquivo de comparação
            punch_file = os.path.dirname(os.path.abspath(__file__)).replace('wizard', 'data') + '/ponto_super.txt'
            self.create_super(content, punch_file)
        else:
            # Arquivo de comparação
            punch_file = os.path.dirname(os.path.abspath(__file__)).replace('wizard', 'data') + '/ponto.txt'

            self.create_afd(content, punch_file)

        # Retorno para a tela dos pontos
        return {
            "type": "ir.actions.act_window",
            "name": _("Relógio de ponto"),
            "res_model": "punch.clock",
            "domain": [("id", "in", self.env['punch.clock'].search([]).ids)],
            "view_mode": "tree,form",
        }

    def create_super(self, content, punch_file):
        if not os.path.exists(punch_file): # Primeiro registro
            with open(punch_file, 'w') as file: # w significa write
                # Cria um arquivo de ponto e copia o arquivo escolhido para armazenar os pontos
                for index, line in enumerate(content):
                    if index != (len(content) - 1):
                        file.write(line + '\n')
                    else:
                        file.write(line)
            content_var = content
        else: # Próximos registros
            # Edita o arquivo txt apenas adicionando as linhas novas
            with open(punch_file, 'r') as file: # r significa read
                lines = len(file.readlines())
                content_var = content[lines:] # Variável content recebe apenas as novas linhas de ponto

            # Arquivo recebe as novas linhas de ponto
            with open(punch_file, 'a') as file: # a significa append
                file.write('\n')
                for index, line in enumerate(content):
                    if index != (len(content) - 1):
                        file.write(line + '\n')
                    else:
                        file.write(line)

        for index, line in enumerate(content_var): # Linhas que contém registro de ponto
            # linhas de 106 caracteres sao apontamentos (I e A)
            if len(line) == 106:
                # Informações referentes a batida do funcionário
                date = line[14:18]+"-"+line[12:14]+"-"+line[10:12]
                time = line[18:20] + ":" + line[20:22]
                pis = line[24:35]

                # Criação do ponto
                hours, minutes = map(int, time.split(":"))
                employee_id = self.env['hr.employee'].search([('employee_pis', '=', pis)])
                if not employee_id:
                    continue
                punch_clock_id = self.env['punch.clock'].search([
                    ('punch_date', '=', date), ('employee_id', '=', employee_id.id)])
            elif len(line) == 38:
                # Informações referentes à batida do funcionário
                pis = line[23:34]
                time = line[18:20] + ":" + line[20:22]
                date = line[14:18]+"-"+line[12:14]+"-"+line[10:12]

                # Verifica se tem ponto criado nesse dia
                employee_id = self.env['hr.employee'].search([('employee_pis', '=', pis)])
                if not employee_id:
                    continue
                hours, minutes = map(int, time.split(":"))
                punch_clock_id = self.env['punch.clock'].search(
                    [('punch_date', '=', date), ('employee_id', '=', employee_id.id)])
            else:
                continue

            # Criação do horário do ponto
            vals_list = {
                'time_punch': time,
                'status': 'valid',
                'seconds': (hours * 3600) + (minutes * 60)
            }
            child_punch = self.env['punch.clock.time'].create(vals_list)

            # Caso não tenha um punch_clock nessa data para o funcionário, é criado um novo e adicionado o time
            if not punch_clock_id:
                vals_list = {
                    'employee_id': employee_id.id,
                    'punch_date': date,
                    'punch_ids': [child_punch.id],
                    'employee_pis': employee_id.employee_pis
                }
                self.env['punch.clock'].create(vals_list)
            else: # Caso já tenha sido criado, ele só adiciona o time dentro
                punch_clock_id.write({'punch_ids': [[4, child_punch.id, False]]})
            if index == (len(content_var) - 1):
                return

    def create_fabrica(self, content, punch_file):
        if not os.path.exists(punch_file): # Primeiro registro
            with open(punch_file, 'w') as file: # w significa write
                # Cria um arquivo de ponto e copia o arquivo escolhido para armazenar os pontos
                for index, line in enumerate(content):
                    if index != (len(content) - 1):
                        file.write(line + '\n')
                    else:
                        file.write(line)
            content_var = content
        else: # Próximos registros
            # Edita o arquivo txt apenas adicionando as linhas novas
            with open(punch_file, 'r') as file: # r significa read
                lines = len(file.readlines())
                content_var = content[lines:] # Variável content recebe apenas as novas linhas de ponto

            # Arquivo recebe as novas linhas de ponto
            with open(punch_file, 'a') as file: # a significa append
                file.write('\n')
                for index, line in enumerate(content):
                    if index != (len(content) - 1):
                        file.write(line + '\n')
                    else:
                        file.write(line)

        for index, line in enumerate(content_var): # Linhas que contém registro de ponto
            if len(line) == 118:
                # Informações referentes a batida do funcionário
                # first_space = line.find(" ")
                # last_space = line.rfind(" ")
                # employee_name = line[first_space + 1:last_space].strip()
                date = line[10:20]
                time = line[21:26]
                cpf = line[35:46]

                # Criação do ponto
                hours, minutes = map(int, time.split(":"))
                employee_id = self.env['hr.employee'].search([
                    ('cpf', '=', cpf), ('employee_pis', 'not like', '%d%')])
                if not employee_id:
                    continue
                punch_clock_id = self.env['punch.clock'].search([
                    ('punch_date', '=', date), ('employee_id', '=', employee_id.id)])
            elif len(line) == 50:
                # Informações referentes à batida do funcionário
                cpf = line[34:45]
                date = line[10:20]
                time = line[21:26]

                # Criação do ponto
                employee_id = self.env['hr.employee'].search([
                    ('cpf', '=', cpf), ('employee_pis', 'not like', '%d%')])
                if not employee_id:
                    continue
                hours, minutes = map(int, time.split(":"))
                punch_clock_id = self.env['punch.clock'].search(
                    [('punch_date', '=', date), ('employee_id', '=', employee_id.id)])
            else:
                continue

            # Criação do horário do ponto
            vals_list = {
                'time_punch': time,
                'status': 'valid',
                'seconds': (hours * 3600) + (minutes * 60)
            }
            child_punch = self.env['punch.clock.time'].create(vals_list)

            # Caso não tenha um punch_clock nessa data para o funcionário, é criado um novo e adicionado o time
            if not punch_clock_id:
                vals_list = {
                    'employee_id': employee_id.id,
                    'punch_date': date,
                    'punch_ids': [child_punch.id],
                    'employee_pis': employee_id.employee_pis
                }
                self.env['punch.clock'].create(vals_list)
            else: # Caso já tenha sido criado, ele só adiciona o time dentro
                punch_clock_id.write({'punch_ids': [[4, child_punch.id, False]]})
            if index == (len(content_var) - 1):
                return

    def create_afd(self, content, punch_file):
        machine_info = []

        for i in range(7): # As 7 primeiras linhas dizem respeito ao relogio
            machine_info.append(content[i])
            content.remove(content[0])
        if not os.path.exists(punch_file): # Primeiro registro
            with open(punch_file, 'w') as file: # w significa write
                # Cria um arquivo de ponto e copia o arquivo escolhido para armazenar os pontos
                for index, line in enumerate(content):
                    if index != (len(content) - 1):
                        file.write(line + '\n')
                    else:
                        file.write(line)
            content_var = content

        else: # proximos registros

            # edita o arquivo txt apenas adicionando as linhas novas
            with open(punch_file, 'r') as file: # r significa read
                lines = len(file.readlines())
                content_var = content[lines:] # variável content_var recebe apenas as novas linhas de ponto

            # arquivo recebe as novas linhas de ponto
            with open(punch_file, 'a') as file: # a significa append
                file.write('\n')
                for index, line in enumerate(content):
                    if index != (len(content) - 1):
                        file.write(line + '\n')
                    else:
                        file.write(line)

        # existem alguns registros que contem o nome do colaborador concatenado, e um caracter na string,
        # aqui a string é verificada e limpa
        character_to_remove = []
        for rec in content_var:
            if len(rec) > 34:
                rec = rec[0:35]
                for character in rec:
                    if character.isalpha():
                        character_to_remove.append(character)
                for i in character_to_remove:
                    rec = rec.replace(i, '')

        # aqui os dados da string são tratados e criados
        for line in content_var:
            punch_id = int(line[0:9])
            punch_date = datetime.datetime.strptime(line[10:18], '%d%m%Y').date()
            if any(char.isalpha() for char in line):
                employee_pis = str(line[24:35])
            else:
                employee_pis = str(line[23:])
            hour = line[18:20]
            minute = line[20:22]
            seconds = (int(hour) * 3600) + (int(minute) * 60)
            existent_punch_in_day = self.env['punch.clock'].search([
                ('employee_pis', '=', employee_pis), ('punch_date', '=', punch_date)])
            if not existent_punch_in_day:
                employee_id = self.env['hr.employee'].search([('employee_pis', '=', employee_pis)]).id
                father_vals = {
                    'original_afd_id': punch_id,
                    'punch_date': punch_date,
                    'employee_pis': employee_pis,
                    'employee_id': employee_id if employee_id else False,
                }
                punch_id = self.env['punch.clock'].create(father_vals)

                child_vals = {
                    'day_id': punch_id.id,
                    'status': 'valid',
                    'time_punch': "{:02d}:{:02d}".format(int(hour), int(minute)),
                    'seconds': seconds,
                }
            else:
                child_vals = {
                    'day_id': existent_punch_in_day.id,
                    'status': 'valid',
                    'time_punch': "{:02d}:{:02d}".format(int(hour), int(minute)),
                    'seconds': seconds,
                }
            self.env['punch.clock.time'].create(child_vals)

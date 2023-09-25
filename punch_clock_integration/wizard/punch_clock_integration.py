import datetime
from odoo import models, fields,_
import base64
import os


class PunchClockIntegration(models.TransientModel):
    _name = 'punch.clock.integration'

    afd_file = fields.Binary(string="Arquivo AFD")

    def criar(self):
        machine_info = []
        content = base64.b64decode(self.afd_file)
        content = content.decode('utf-8').split('\r\n')
        punch_file = os.path.dirname(os.path.abspath(__file__))+'\\ponto.txt'

        for i in range(7):
            machine_info.append(content[i])
            content.remove(content[0])
        if not os.path.exists(punch_file): #primeiro registro
            with open(punch_file, 'w') as file: #w significa write
                # Cria um arquivo de ponto e copia o arquivo escolhido para armazenar os pontos
                for index,line in enumerate(content):
                    if index != (len(content)-1):
                        file.write(line+'\n')
                    else:
                        file.write(line)
            # as 4 primeiras linhas dizem respeito ao relogio(no txt são 7 linhas mas ao testar pegou os registros que não
            # deveriam ser retornados por isso aqui na função so pego 4 linhas), por isso são salvas e removidas da lista de ponto

        else:#proximos registros
            # edita o arquivo txt apenas adicionando as linhas novas
            with open(punch_file, 'r') as file: #r significa read
                lines = len(file.readlines())
                content = content[lines:]# variável content recebe apenas as novas linhas de ponto

            #arquivo recebe as novas linhas de ponto
            with open(punch_file, 'a') as file: #a significa append
                file.write('\n')
                for index,line in enumerate(content):
                    if index != (len(content)-1):
                        file.write(line+'\n')
                    else:
                        file.write(line)

        # existem alguns registros que contem o nome do colaborador concatenado, e um caracter na string,
        # aqui a string é verificada e limpa
        character_to_remove = []
        for rec in content:
            if len(rec) > 34:
                rec = rec[0:35]
                for character in rec:
                    if character.isalpha():
                        character_to_remove.append(character)
                for i in character_to_remove:
                    rec = rec.replace(i, '')

        # aqui os dados da string são tratados e criados
        list = []
        for line in content:
            punch_id = int(line[0:9])
            punch_datetime = datetime.datetime.strptime(line[10:22], '%d%m%Y%H%M')
            if any(char.isalpha() for char in line):
                employee_pis = str(line[24:35])
            else:
                employee_pis = str(line[23:])

            employee_id = self.env['hr.employee'].search([('employee_pis','=',employee_pis)]).id
            vals = {
                'punch_id': punch_id,
                'punch_datetime': punch_datetime,
                'employee_pis': employee_pis,
                'employee_id': employee_id if employee_id else False,
            }
            list.append(vals)
        punch_ids = self.env['punch.clock'].create(list)

        #atribuição de valores do campo de horas virtuais provavelmente estará presente nessa parte do código
        #deve ser atribuído quantos segundos bonus ele tem, no campo virtual_seconds do hr employee


        return {
            "type": "ir.actions.act_window",
            "name": _("Relógio de ponto"),
            "res_model": "punch.clock",
            "domain": [("id", "in", punch_ids.ids)],
            "view_mode": "tree,form",
            "context": self.env.context
        }
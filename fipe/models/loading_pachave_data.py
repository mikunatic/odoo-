from odoo import api, models, fields
import pymssql


class PachaveData(models.Model):
    _name = "pachave"
    _inherit = _name

    @api.model
    def _import_pachave_data(self):
        conn = pymssql.connect('192.168.1.2', 'sa', 'Sql2018', 'SuperGlass')
        cursor = conn.cursor()
        string = "select distinct mt_pachave, MT_MARCA from HT_DBGM_DMT where mt_marca != '' order by 1"
        cursor.execute(string)
        row = cursor.fetchone()
        while row is not None:
            nome = str(row[0]).rstrip("\x00")
            if row[1].__eq__("MERCEDES BENZ"):
                marca = "Mercedes-Benz"
            elif row[1].__eq__("CITROEN"):
                marca = "Citroën"
            else:
                marca = str(row[1]).rstrip("\x00")
            fipe_ids = self.env['fipe'].search(
                [('name', 'ilike', nome), ('marca', 'ilike', marca)])

            if not fipe_ids:
                row = cursor.fetchone()
                continue

            valslist = {
                'name': nome,
                'fipe_ids': [(6, 0, fipe_ids.ids)]
            }

            exist_name = self.search([('name', '=like', nome)])

            if not exist_name:
                super(PachaveData, self).create(valslist)
            else:
                for rec in exist_name.fipe_ids:
                    fipe_ids += rec
                exist_name.write(exist_name.id, {
                    'name': nome,
                    'fipe_ids': [(6, 0, fipe_ids.ids)]
                })
            row = cursor.fetchone()

# Copyright (C) 2013  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Módulo fiscal brasileiro (Extensão)",
    "summary": "Brazilian fiscal core module.",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "Matheus Prado de Melo",
    "maintainers": ["Matheus Prado"],
    "website": "https://github.com/OCA/l10n-brazil",
    "version": "14.0.7.4.1",
    "depends": [
        "l10n_br_fiscal",
        "account"
    ],
    "data": [
        "views/tax.xml",
        "views/operation_line.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

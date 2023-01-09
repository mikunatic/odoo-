# -*- coding: utf-8 -*-
{
    'name': 'Account Inherit',
    'category': 'Accounting',
    'summary': 'Account Inherit',
    'version': '1.0',
    'description': """Account Inherit""",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_extended_view.xml',
        'wizard/account_wiz_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

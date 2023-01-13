{
    'name': 'Inherits',
    'category': 'Inherits',
    'summary': 'Inherits',
    'version': '1.0',
    'description': """Inherit""",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_extend_view.xml',
        'views/ger_proc_inherit_view.xml',
        'views/cadastro_cheque_view.xml',
        'views/lote_inherit_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

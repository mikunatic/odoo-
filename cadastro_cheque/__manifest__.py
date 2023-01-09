{
    'name': 'Cadastro de Cheques',
    'category': 'Cheque',
    'summary': 'Cadastro de Cheque',
    'version': '1.0',
    'description': """Cadastro de Cheque""",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/cadastro_cheque_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
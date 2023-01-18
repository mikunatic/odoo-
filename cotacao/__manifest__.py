{
    'name': 'Cotação',
    'category': 'Vendas',
    'summary': 'Cotação',
    'version': '1.0',
    'description': """Cadastro de Cotações""",
    'depends': ['product','sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cotacao_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

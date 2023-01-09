{
    'name': 'Fipeglass',
    'version': '15.0.0.0',
    'category': 'Product',
    'sequence': 14,
    'author': 'Marcelo Barbosa dos Santos',
    "contributors": [
        "Matheus Prado de Melo"
    ],
    'license': 'LGPL-3',
    'summary': '',
    'depends': ['product'],
    'data': [
        'views/fipe_view.xml',
        'views/product_view.xml',
        'views/pachave_view.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/autogenerate.xml',
        'data/loading_pachave.xml'
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

{
    'name': 'Payment Inherit',
    'category': 'Payment',
    'summary': 'Payment Inherit',
    'version': '1.0',
    'description': """Payment Inherit""",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_extend_view.xml',
        'views/ger_proc_inherit_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

{
    'name': 'Pontos',
    'version': '14.0.1.0.1',
    'summary': "",
    'description': "",
    'category': '',
    'author': 'Thiago Francelino Santos',
    'contributors': [
        'Mila Feitosa Martins',
        'Gustavo Lourenço',
    ],
    'depends': ['base', 'hr'],
    'external_dependencies': {
        'python': [
            'datetime',
        ],
    },
    'company': 'SUPERGLASS',
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizard/manage_employee_time.xml',
        'wizard/punch_clock_integration_view.xml',
        'views/punch_clock_view.xml',
        'views/hr_employee_view.xml',
        'views/remoteness_view.xml',
        'views/syndicate_view.xml',
        'views/event_view.xml',
        'views/employee_remoteness.xml',
        'views/general_configuration_view.xml',
        'views/virtual_hours.xml',
        'views/autogenerate.xml',
        'wizard/bank_register.xml',
        'data/company.xml',
        'data/function.xml',
        'data/events.xml',
        'data/syndicate.xml',
        'data/remoteness.xml',
        'data/day.xml',
        'data/debit.xml',
        'data/credit.xml',
        'data/hours.xml',
        # 'data/workday.xml',
        'wizard/wizard_create_punch_time_view.xml',
        'wizard/create_justification_view.xml',
        'wizard/employees_by_interval_view.xml',
        'wizard/manual_point_view.xml',
        'wizard/punch_disregard_view.xml',
        'data/general_configuration.xml',
    ],
    'license': 'LGPL-3',
    'application': True
}

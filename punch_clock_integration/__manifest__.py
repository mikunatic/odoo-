{
    'name': 'punch_clock_integration',
    'version': '14.0.1.0.1',
    'summary': "",
    'description': "",
    'category': '',
    'author': 'Thiago Francelino Santos',
    'contributors': [
        'Mila Feitosa Martins',
        'Gustavo Lourenço',
    ],
    'depends': ['base','hr'],
    'company': 'SUPERGLASS',
    'data': [
        'security/ir.model.access.csv',
        'views/punch_clock_view.xml',
        'wizard/punch_clock_integration_view.xml',
        'wizard/punch_time_view.xml',
        'wizard/manage_employee_time.xml',
        'wizard/manual_point_view.xml',
        'wizard/add_justification_view.xml',
        'views/hr_employee_view.xml',
        'views/remoteness_view.xml',
        'views/syndicate_view.xml',
        'views/event_view.xml',
        'views/work_week.xml',
        'views/justification_view.xml',
        'views/general_configuration_view.xml',
        'data/function.xml',
        'data/events.xml',
        'data/hours.xml',
        'data/employee_company.xml',
        'data/syndicate.xml',
        'data/employee.xml',
        'data/remoteness.xml',
        'data/day.xml',
        'data/holidays.xml',
        'data/general_configuration.xml',
    ],
    'license': 'LGPL-3',
    'application':True
}
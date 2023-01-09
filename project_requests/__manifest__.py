{
    'name': "Projetos e Solicitações",
    'summary': "Organização para realização de projetos e solicitações para toda a empresa",
    'author': "Thalles Rodrigues",
    "contributors": [
        "Matheus Prado de Melo"
        "Marcelo Barbosa dos Santos"
    ],
    'website': "https://superglass.com.br/",
    'category': 'Uncategorized',
    'version': '15.0.1.0.0',
    'depends': ['product', 'hr'],
    'data': [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/project_request_view.xml",
        "wizards/response_request_view.xml",
        "views/category_request_view.xml",
        "views/recurring_view.xml",
        "views/autogenerate.xml",
        "wizards/update_project_status.xml"
    ],
    'installable': True,
    'application': True,
}

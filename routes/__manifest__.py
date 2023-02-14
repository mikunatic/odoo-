{
    'name': "Rotas",
    'summary': "Criação de Rotas",     
    'author': "Julia Pimenta, Thalles Rodrigues, Vinicius Miranda",
    "contributors": [
        "Matheus Prado de Melo"
        "Marcelo Barbosa dos Santos"
    ],
    'website': "https://vidroshima.com.br/",
    'category': 'Uncategorized',
    'version': '14.0.1.0.0',
    'depends': ['base', 'product'],
    'data': [ 
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/criacao_rotas_view.xml",
        "views/res_partner_view.xml",
        "data/routes_loading_data.xml",
        "data/partner_loading_data.xml"
        ],
    #'demo': ['demo.xml'],
    'installable': True,
    'application': True,
}
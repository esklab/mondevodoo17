{
    'name': 'Type de projet',
    'version': '1.0',
    'description': 'Gestion des Type de projet',
    'summary': 'Gestion des Type de projet',
    'author': 'Thomas ATCHA',
    'website': 'https://erptogo.net',
    'license': 'LGPL-3',
    'category': 'Project',
    'depends': [
        'base','project'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_view.xml',
        'views/project_exp.xml',
        'data/data.xml',
    ],
    'auto_install': False,
    'application': False,
}
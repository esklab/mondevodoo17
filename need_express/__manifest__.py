{
    'name': 'Need of express',
    'version': '1.0',
    'description': 'Need of express',
    'summary': 'Need of express',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'product',
        'hr',
        'purchase',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/need_express_views.xml',
        'views/need_express_action.xml',
    ],
    'auto_install': False,
    'application': True,
}
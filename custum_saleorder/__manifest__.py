{
    'name': 'Custom Facture 2',
    'version': '3.0',
    'description': 'Custom Facture 2',
    'summary': 'Custom Facture 2',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'account',
        'sale_management',
        'acs_hms_hospitalization'
    ],
    "data": [
        "views/account_move_views.xml",
        "views/sale_order_views.xml"
    ],
    'auto_install': False,
    'application': True,
}
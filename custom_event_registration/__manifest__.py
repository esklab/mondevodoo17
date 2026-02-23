{
    'name': 'Custom POS',
    'version': '2.0',
    'description': 'Custom POS',
    'summary': 'Custom POS',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'point_of_sale',
        'hotel_management_odoo',
    ],
    "data": [
        "views/event_registration_views.xml"
    ],
    'auto_install': False,
    'application': True,
}
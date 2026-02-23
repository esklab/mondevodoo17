{
    'name': 'Prescription to Consumables',
    'version': '17.0',
    'description': 'Prescription to Consumables',
    'summary': 'Prescription to Consumables',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'acs_hms',
        'acs_hms_hospitalization',
    ],
    "data": [
        'views/prescription_order_views.xml'
    ],
    'auto_install': False,
    'application': True,
}
{
    'name': 'Custom ResCompany',
    'version': '1.0',
    'description': 'Active Automatically plan Comptable Togo',
    'summary': 'Active Automatically plan Comptable Togo',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'website_slides',
        'th_ift_web',
        'th_ift_reservation',
    ],
    "data": [
        "data/data.xml",
        "views/slide_channel_views.xml",
        'security/ir.model.access.csv'
    ],
    'auto_install': False,
    'application': True,
}
{
    'name': 'Custom Elearning TgCf',
    'version': '1.0',
    'description': 'Custom Elearning TgCf',
    'summary': 'Custom Elearning TgCf',
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
        "security/ir.model.access.csv",
        "views/slide_channel_partner_views.xml"
    ],
    'auto_install': False,
    'application': True,
}
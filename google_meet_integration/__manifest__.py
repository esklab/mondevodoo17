{
    'name': "Google Meet Integration",
    'summary': "Intégration de Google Meet dans le calendrier Odoo",
    'version': "1.0",
    'category': "Tools",
    'author': "Charles Meheza EFALO",
    'website': "http://devcharles.com",
    'depends': ['base', 'calendar', 'google_calendar'],
    'data': [
        'views/res_users_views.xml',
        'views/google_calendar_event.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}

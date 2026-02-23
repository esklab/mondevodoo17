{
    'name': 'hospi report',
    'version': '1.0',
    'description': 'hospi report',
    'summary': 'hospi report',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'acs_hms_hospitalization',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hospitalisation_report_views.xml",
        "reports/hospitalisation_report_views.xml",
    ],
    'auto_install': False,
    'application': True,
}
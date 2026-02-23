{
    'name': 'Stock report',
    'version': '1.0',
    'description': 'Stock report',
    'summary': 'Stock report',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'stock',
    ],
    "data": [
        "views/stock_report_wizard_views.xml",
        "reports/stock_report_wizard_report.xml"
    ],
    'auto_install': False,
    'application': True,
}
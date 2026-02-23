{
    'name': 'BOAD_Allocations',
    'version': '2.0',
    'description': 'BOAD_Allocations',
    'summary': 'BOAD_Allocations',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'hr_holidays',
        'hr_payroll',
        'th_custum_payroll',
    ],
    "data": [
        "views/hr_contract_views.xml"
    ],
    'auto_install': False,
    'application': True,
}

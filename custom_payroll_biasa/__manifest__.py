{
    'name': 'Custum Payroll BIASA',
    'version': '1.0',
    'description': 'Custum Payroll BIASA',
    'summary': 'Custum Payroll BIASA',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'hr_payroll',
        'th_custum_payroll'
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/hr_contract_views.xml",
        "views/hr_salary_views.xml",
    ],
    'auto_install': False,
    'application': True,
}
{
    'name': 'Custum Payroll BOAD',
    'version': '1.0',
    'description': 'Custum Payroll BOAD',
    'summary': 'Custum Payroll BOAD',
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
        #'data/data_paie_rule.xml'
    ],
    'auto_install': False,
    'application': True,
}
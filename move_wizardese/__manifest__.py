{
    'name': 'Factures Assurances',
    'version': '1.0',
    'description': 'Factures Assurances',
    'summary': 'Factures Assurances',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'account_accountant',
	    'acs_hms_insurance',
    ],
    "data": [
        "security/ir.model.access.csv",
        "reports/report_insurance.xml",
        "views/hospitalisation_report_views.xml",
    ],
    'auto_install': False,
    'application': True,
}
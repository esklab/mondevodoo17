# -*- coding: utf-8 -*-
{
    'name': 'Paie TOGO',
    'version': '1.2.0',
    'price': 15.99,
    'currency': 'EUR',
    'license': 'AGPL-3',
    'summary': """
       Ajout des champs de rubriques de paie version 2.2.1 n
    """,
    'category': 'Paie',
    'author': 'MAONO',
    'maintainer': 'MAONO DEV',
    'company': 'Thomas ATCHA',
    'website': 'https://digitaltg.net',
    'depends': ['base', 'hr', 'hr_payroll', ],
    'data': [
        'security/ir.model.access.csv',        
        'data/data.xml',
        'reports/fiche_de_paie.xml',
        'views/contract.xml',
        # 'views/employee_fields_view.xml',
        'reports/report_livre_mensuel.xml',
        'reports/report_livre_annuel.xml',
        'wizards/payroll_pdf_report.xml',
        'wizards/livre_annuel_pdf.xml',
        # 'wizards/dnr_wizard_view.xml',
        'wizards/payroll_report_wiz.xml',
        # 'views/periode_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}

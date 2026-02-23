{
    'name': 'Custom Labo States',
    'version': '1.0',
    'description': 'Custom Labo States',
    'summary': 'Custom Labo States',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'acs_laboratory',
    ],
    "data": [
        "views/acs_patient_laboratory_sample_views.xml",
        "views/patient_laboratory_test_views.xml"
    ],
    'auto_install': False,
    'application': True,
}
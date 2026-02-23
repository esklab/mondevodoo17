{
    'name': 'Custom report ',
    'version': '1.0',
    'description': 'Custom report ',
    'summary': 'Custom report ',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'acs_hms',
    ],
    "data": [
        'reports/report_appointments_by_doctor.xml',
        'views/hms_appointment_views.xml',
    ],
    'auto_install': False,
    'application': True,
}
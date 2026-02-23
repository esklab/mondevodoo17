{
    'name': 'Custom Booking type',
    'version': '3.0',
    'description': 'Custom Booking type',
    'summary': 'Custom Booking type',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'appointment',
    ],
    'data': [
        #'views/custom_appointment_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # 'custom_booking_type/static/src/js/custom_appointment.js',
        ],
    },
    'auto_install': False,
    'application': True,
}

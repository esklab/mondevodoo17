{
    'name': 'Bulletin',
    'version': '1.0',
    'description': 'Bulletin',
    'summary': 'Bulletin Management',
    'author': 'maono',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
    ],
    'data': [ 
        'security/ir.model.access.csv',
        'views/school_grade_views.xml',
        'views/school_report_card_views.xml',
        'views/school_student_views.xml',
        'views/school_subject_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'bulletin/static/css/style.css',
        ],
    },
    'auto_install': False,
    'application': True,
}
# -*- coding: utf-8 -*-
###################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar (<https://www.inteslar.com>).
#    Author:   (<https://www.inteslar.com>)
#
###################################################################################
{
    'name': 'Freight Management',
    'version': '17.0',
    'category': 'freight',
    'price': 800,
    'currency': 'USD',
    'license': 'OPL-1',
    'live_test_url':'https://www.youtube.com/watch?v=66lKp26x75k',
    'website':'https://www.inteslar.com',
    'images': ['static/description/banner.jpg'],
    'author':'inteslar',
    'summary': 'Manage freight forwarding shipping activities in Air Ocean and Land',
    'description': """
Key Features
------------
* Freight Management
        """,
    'depends': ['base', 'base_setup', 'account', 'product', 'contacts', 'mail', 'board', 'calendar',
                'web', 'sale_management', 'website', 'portal', 'hr', 'stock', 'fleet'],
    'data': [
        'data/freight_data.xml',
        'security/ir.model.access.csv',
        'report/bill_of_lading.xml',
        'report/airway_bill.xml',
        'views/freight_report.xml',
        'wizard/register_invoice_freight_view.xml',
        'views/freight_view.xml',
        'views/booking_view.xml',
        'views/freight_templates.xml',
        'views/product_view.xml',
        'views/menuitem.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'assets': {
    'web.assets_backend': [
            '/freight/static/src/css/dashboard.scss',
            '/freight/static/lib/dataTables/datatables_min.scss',
            '/freight/static/lib/dataTables/buttons_dataTables_min.scss',
            '/freight/static/lib/charts/Chart_min.js',
            '/freight/static/lib/charts/Chart_bundle_min.js',
            '/freight/static/lib/dataTables/datatables_min.js',
            '/freight/static/lib/dataTables/dataTables_buttons_min.js',
            '/freight/static/lib/dataTables/buttons_flash_min.js',
            '/freight/static/lib/dataTables/buttons_html5_min.js',
            '/freight/static/lib/dataTables/buttons_print_min.js',
            '/freight/static/lib/dataTables/pdfmake_min.js',
            '/freight/static/lib/dataTables/vfs_fonts.js',
            '/freight/static/lib/dataTables/jszip_min.js',
            '/freight/static/lib/dataTables/buttons_bootstrap_min.js',
            '/freight/static/lib/dataTables/buttons_bootstrap4_min.js',
            '/freight/static/lib/dataTables/buttons_colVis_min.js',
            '/freight/static/lib/jsPdf/jspdf_min.js',
            '/freight/static/lib/jsPdf/jspdf_debug.js',
            '/freight/static/src/js/freight_dashboard.js',
            'freight/static/src/xml/**/*',
        ],
        'web.assets_frontend': [
            '/freight/static/src/js/website_booking.js',
            ],
    #    'web.assets_qweb': [
    #        'freight/static/src/xml/**/*',
    #    ],
    }
}

{
    'name': 'Cashpay Payment Acquirer',
    'version': '1.0',
    'description': """Cashpay Payment Acquirer""",
    'summary': 'Payment Acquirer: Cashpay implementation',
    'author': 'Thomas ATCHA',
    'website': 'https://erptogo.net',
    'license': 'LGPL-3',
    'category': 'Accounting/Payment Acquirers',
    'depends': [
          'payment'
    ],
    'data': [
        'views/payment_cashpay_template.xml',
        'views/payment_view.xml',
        'data/payment_acquirer_data.xml',
    ],
    'auto_install': False,
    'unistall_hook':'uninstall_hook',
    'application': True,
}
{
    'name': 'Dynamic Field Mapping',
    'version': '1.0.0',
    'category': 'Extra Tools',
    'summary': """Dynamic field mapping between two models in Odoo involves setting up mechanisms to automatically transfer or update data from one model to another. This can be useful in various scenarios, such as synchronizing data between CRM leads and sales orders, sales orders and Invoice or any other custom models. In Odoo, dynamic field mapping refers to the ability to map fields between different models dynamically, allowing for greater flexibility and adaptability in data handling and process automation. This can be particularly useful when integrating Odoo with other systems or when working with custom modules that require specific field mappings that can change over time.Custom Field Mapping,Dynamic Data Mapping,Dynamic Model Mapping,Model Field Mapping,Dynamic Attribute Mapping,Flexible Field Mapping,Customizable Data Mapping,
field mapping from sale to purchase, field mapping from sales to delivery,field mapping from purchase to receipt
field mapping from helpdesk ticket to repair,field mapping from helpdesk ticket to project task
field mapping from helpdesk ticket to refund invoice,field mapping from helpdesk ticket to return order
field mapping from crm to rental,field mapping from sales to project task
field mapping from purchase to vendor bill,field mapping from crm to sales
""",
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/dynamic_field_mapping.xml',
    ],
    'images': ['static/description/cover.gif'],
    'author': 'Vraja Technologies',
    'website': 'https://www.vrajatechnologies.com',
    'live_test_url': 'https://www.vrajatechnologies.com/contactus',
    'installable': True,
    'application': True,
    'autoinstall': False,
    'price': '15',
    'currency': 'EUR',
    'license': 'OPL-1',
}

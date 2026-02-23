{
    'name': 'Gestion des Clients',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Gestion et validation des clients',
    'description': """
        Module de gestion des clients avec processus de validation :
        - Workflow de validation des clients
        - Notifications automatiques
        - Contrôles de sécurité
    """,
    'depends': ['base', 'mail', 'contacts'],
    'data': [

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
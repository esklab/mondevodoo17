{
    'name': 'Gestion des Prix - Acconage et Relevage',
    'version': '1.0',
    'summary': 'Gestion des prix d\'acconage et relevage par type de conteneur et catégorie d\'article',
    'sequence': 10,
    'description': """
        Module pour la gestion des prix d'acconage et de relevage :
        - Basé sur les catégories d'articles et les types de conteneurs
        - Historisation annuelle des prix
        - Gestion des prix par défaut
    """,
    'category': 'Operations',
    'author': 'BOX AFRICA',
    'depends': [
        'base', 'product', 'sales_team','sale_management',
    ],  # Dépend du module "product" pour les catégories d'articles
    'data': [
        'security/dock_price_security.xml',
        'security/ir.model.access.csv',
        'views/dock_category_views.xml',
        'views/product_template_views.xml',
        'views/dock_price_views.xml',
        'views/dock_transport_zone_views.xml',
        'views/dock_price_menu.xml',
        'views/order_universe_views.xml',
        'views/product_category_views.xml',
        'views/sale_order_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
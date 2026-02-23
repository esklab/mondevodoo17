{
    'name': 'Moteur de Workflow',
    'version': '17.0.1.0.0',
    'summary': 'Summery',
    'description': 'Moteur de workflow pour la validation de tous types de flux',
    'category': 'Tools',
    'author': '(BOX AFRICA)',
    'website': 'htts://www.box.africa',
    'license': 'OPL-1',
    'depends': [
        'base'
    ],
    'data': [
        'security/workflow_groups.xml',
        'security/ir.model.access.csv',
        'security/workflow_rules.xml',
        'views/workflow_model_view.xml',
        'views/workflow_history_view.xml',
        'views/workflow_state_view.xml',
        'views/workflow_transition_view.xml',
        'views/workflow_trash_view.xml',
        'views/menu_view.xml',
    ],
    'installable': True,
    'auto_install': False
}

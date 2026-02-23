# -*- coding: utf-8 -*-
{
    'name': 'Note de frais BOAD',
    'version': '1.2',
    'summary': """This module will add a record to store  notes de frais details""",
    'description':  """Module pour generer les notes de frais pour la BOAD""",
    'category': 'Custom',
    'license': 'LGPL-3',
    'author': 'Charles Meheza Efalo',
    'website': 'devcharles.com',
    'depends': ['base', 'project'],
    'data': [
        'views/action_open_note_frais_form.xml',

        'views/view_note_frais_form.xml',
        'views/view_menu.xml',

    ],

    'installable': True,
}
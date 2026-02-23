# -*- coding: utf-8 -*-
###################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar (<https://www.inteslar.com>).
#    Author:   (<https://www.inteslar.com>)
#
###################################################################################
{
    'name': 'Custom Freight Management',
    'version': '17.0',
    'category': 'freight',
    'author':'maono',
    'depends': [
        'base',
        'freight',
        'project'
    ],
    'data': [
        'security/freight_operator.xml',
        'data/stage_data.xml',
        'views/freight_view.xml',
        # 'views/freight_tasks.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}

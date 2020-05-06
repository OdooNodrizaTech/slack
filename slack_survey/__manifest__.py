# -*- coding: utf-8 -*-
{
    'name': 'Slack Survey',
    'version': '12.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'survey', 'slack'],
    'data': [
        'data/slack_data.xml'
    ],    
    'installable': True,
    'auto_install': False,    
}
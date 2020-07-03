# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Slack',
    'version': '12.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base','sale'],
    'data': [
        'data/slack_data.xml',
        'views/res_users.xml',
    ],
    'external_dependencies': {
        'python3' : ['slackclient'],
    },    
    'installable': True,
    'auto_install': False,    
}
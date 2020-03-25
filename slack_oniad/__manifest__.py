# -*- coding: utf-8 -*-
{
    'name': 'Slack Oniad',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base', 'crm', 'slack'],
    'data': [
        'data/ir_cron.xml',
    ],    
    'installable': True,
    'auto_install': False,    
}
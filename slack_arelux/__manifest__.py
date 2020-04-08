# -*- coding: utf-8 -*-
{
    'name': 'Slack Arelux',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base', 'sale', 'account', 'delivery', 'slack', 'picking_arelux', 'arelux_partner_questionnaire'],
    'data': [
        'data/slack_data.xml',
        'data/ir_cron.xml'
    ],    
    'installable': True,
    'auto_install': False,    
}
# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    slack_member_id = fields.Char(
        string='Slack Memeber Id'
    )
    slack_mail_message = fields.Boolean( 
        string='Recibir mensajes de email'
    )
    
    @api.multi
    def action_test_slack(self):
        if self.slack_member_id!=False:                                        
            attachments = [
                {                    
                    "title": 'Esta es una prueba del usuario *'+str(self.name)+'*',                        
                    "color": "#36a64f",                                            
                    "text": "Texto de prueba",                    
                }
            ]
            slack_message_vals = {
                'attachments': attachments,
                'model': self._inherit,
                'res_id': self.id,            
                'channel': self.slack_member_id                                                          
            }                        
            slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)    
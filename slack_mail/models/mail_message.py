# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'
    
    @api.one
    def generate_auto_starred_slack(self, user_id):
        if user_id.id>0 and user_id.slack_member_id!=False and user_id.slack_mail_message==True:
            web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            
            if self.record_name!=False:
                attachments = [
                    {                    
                        "title": 'Nuevo mensaje',
                        "text": str(self.record_name.encode('utf-8')),                        
                        "color": "#36a64f",                                            
                        "footer": str(self.author_id.name.encode('utf-8')), 
                        "fallback": "Ver mensaje "+str(self.record_name.encode('utf-8'))+' '+str(web_base_url)+"/web?#id="+str(self.res_id)+"&view_type=form&model="+str(self.model),                                    
                        "actions": [
                            {
                                "type": "button",
                                "text": "Ver mensaje "+str(self.record_name.encode('utf-8')),
                                "url": str(web_base_url)+"/web?#id="+str(self.res_id)+"&view_type=form&model="+str(self.model)
                            }
                        ]                    
                    }
                ]                            
                
                slack_message_vals = {
                    'attachments': attachments,
                    'model': self._inherit,
                    'res_id': self.id,
                    'channel': user_id.slack_member_id                                                          
                }                        
                slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
    @api.one
    def generate_notice_message_without_auto_starred_user_slack(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if self.record_name!=False:                                                        
            attachments = [
                {                    
                    "title": 'Nuevo mensaje (Sin aviso a ningun comercial)',
                    "text": str(self.record_name.encode('utf-8')),                       
                    "color": "#ff0000",                                            
                    "footer": str(self.author_id.name), 
                    "fallback": "Ver mensaje "+str(self.record_name.encode('utf-8'))+' '+str(web_base_url)+"/web?#id="+str(self.res_id)+"&view_type=form&model="+str(self.model),                                    
                    "actions": [
                        {
                            "type": "button",
                            "text": "Ver mensaje "+str(self.record_name.encode('utf-8')),
                            "url": str(web_base_url)+"/web?#id="+str(self.res_id)+"&view_type=form&model="+str(self.model)
                        }
                    ]                    
                }
            ]            
            
            slack_message_vals = {
                'attachments': attachments,
                'model': self._inherit,
                'res_id': self.id,
                'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_channel'),                                                         
            }                        
            slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
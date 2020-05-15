# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'
    
    @api.multi
    def _postprocess_sent_message(self, success_pids, failure_reason=False, failure_type=None):
        res = super(MailMail, self)._postprocess_sent_message(success_pids, failure_reason, failure_type)
        if failure_reason==True:
            for item in self:
                if item.state=='exception':
                    attachments = [
                        {                    
                            "title": 'Se ha producido un error al enviar el email',
                            "text": item.subject,                         
                            "color": "#ff0000",
                            "fields": [                    
                                {
                                    "title": "Razon del fallo",
                                    "value": item.failure_reason,
                                    'short': True,
                                },
                                {
                                    "title": "Remitente",
                                    "value": item.email_from,
                                    'short': True,
                                },
                                {
                                    "title": item.model,
                                    "value": item.res_id,
                                    'short': True,
                                },                        
                            ],                                                                                    
                        }
                    ]
                    
                    slack_message_vals = {
                        'attachments': attachments,
                        'model': self._inherit,
                        'res_id': item.id,                                                         
                    }                        
                    slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        #return                                                                                                            
        return res    
# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'
    
    @api.multi
    def _postprocess_sent_message(self, mail_sent=True):
        res = super(MailMail, self)._postprocess_sent_message(mail_sent)
        if mail_sent!=True:
            attachments = [
                {                    
                    "title": 'Se ha producido un error al enviar el email',
                    "text": self.subject.encode('utf-8'),                         
                    "color": "#ff0000",
                    "fields": [                    
                        {
                            "title": "Razon del fallo",
                            "value": self.failure_reason.encode('utf-8'),
                            'short': True,
                        },
                        {
                            "title": "Remitente",
                            "value": self.email_from.encode('utf-8'),
                            'short': True,
                        },
                        {
                            "title": self.model,
                            "value": self.res_id,
                            'short': True,
                        },                        
                    ],                                                                                    
                }
            ]
            
            slack_message_vals = {
                'attachments': attachments,
                'model': self._inherit,
                'res_id': self.id,                                                         
            }                        
            slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
                                                                                                            
        return res
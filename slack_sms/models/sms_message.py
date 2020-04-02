# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class SmsMessage(models.Model):
    _inherit = 'sms.message'

    @api.one    
    def action_send_error_sms_message_message_slack(self, res):
        res_return = super(SmsMessage, self).action_send_error_sms_message_message_slack(res)
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            
        attachments = [
            {                    
                "title": 'Error al enviar el SMS',
                "text": res['error'],                         
                "color": "#ff0000"                                                                                
            }
        ]
        
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_sms_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
        return res_return
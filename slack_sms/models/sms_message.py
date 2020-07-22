# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, api, _


class SmsMessage(models.Model):
    _inherit = 'sms.message'

    @api.one    
    def action_send_error_sms_message_message_slack(self, res):
        res_return = super(SmsMessage, self).action_send_error_sms_message_message_slack(res)
            
        attachments = [
            {                    
                "title": _('Error sending the SMS'),
                "text": res['error'],                         
                "color": "#ff0000"                                                                                
            }
        ]
        vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_sms_channel'),                                                         
        }                        
        self.env['slack.message'].sudo().create(vals)
        # res_return
        return res_return
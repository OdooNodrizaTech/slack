# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.one    
    def action_send_cesce_sale_error_message_slack(self, vals):
        res = super(AccountMoveLine, self).action_send_cesce_sale_error_message_slack(vals)
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                        
        attachments = [
            {                    
                "title": 'Error Cesce Ventas',
                "text": vals['error'],                        
                "color": "#ff0000",                                             
                "fallback": "Ver apunte contable "+str(self.name)+' '+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=account.move.line",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver apunte contable "+str(self.name),
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=account.move.line"
                    }
                ]                    
            }
        ]            
        
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_cesce_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
        return res
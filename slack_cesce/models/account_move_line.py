# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.one
    def write(self, vals):
        #need_slack
        if 'cesce_sale_state' in vals:            
            cesce_sale_state_old = self.cesce_sale_state
        #super                                                               
        return_object = super(AccountMoveLine, self).write(vals)
        #need_slack
        if 'cesce_sale_state' in vals:
            cesce_sale_state = self.cesce_sale_state
            if cesce_sale_state=='sale_error' and cesce_sale_state!=cesce_sale_state_old:
                self.action_send_cesce_sale_error_message_slack()
        #return
        return return_object

    @api.one    
    def action_send_cesce_sale_error_message_slack(self, vals):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                        
        attachments = [
            {                    
                "title": 'Error Cesce Ventas',
                "text": self.cesce_error,                        
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
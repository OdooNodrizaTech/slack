# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    @api.one 
    def action_send_mail_info_real(self):
        return_item = super(ShippingExpedition, self).action_send_mail_info_real()
        #action_send_mail_info_expedition_message_slack
        self.action_send_mail_info_expedition_message_slack()        
        #return
        return return_item
        
    @api.one    
    def action_send_mail_info_expedition_message_slack(self):
        res_return = super(ShippingExpedition, self).action_send_mail_info_expedition_message_slack()
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            
        attachments = [
            {                    
                "title": 'Se ha enviado por email la info de la expedicion',
                "text": self.code,                        
                "color": "#36a64f",                                             
                "fallback": "Ver expedicion "+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=shipping.expedition",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver expedicion",
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=shipping.expedition"
                    }
                ],
                "fields": [
                    {
                        "title": "Albaran",
                        "value": self.picking_id.name,
                        'short': True,
                    },                    
                    {
                        "title": "Transportista",
                        "value": self.carrier_type.title(),
                        'short': True,
                    },                    
                ],                    
            }
        ]            
        
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_almacen_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
        return res_return                                                                            
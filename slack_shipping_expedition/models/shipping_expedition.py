# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'
    
    @api.one
    def write(self, vals):
        #state_old
        state_old = None
        if 'state' in vals:
            state_old = self.state
        #write 
        return_write = super(ShippingExpedition, self).write(vals)                        
        #operations
        if 'state' in vals:
            if self.state=='incidence' and state_old!=self.state:
                self.action_incidence_expedition_message_slack() 
        #return
        return return_write
        
    @api.one    
    def action_incidence_expedition_message_slack(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        
        attachments = [
            {                    
                "title": 'Incidencia en la expedicion',
                "text": self.observations,                        
                "color": "#ff0000",                                             
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
                        "title": "Expedicion",
                        "value": self.code,
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
        
        #channel
        channel = self.env['ir.config_parameter'].sudo().get_param('slack_log_almacen_channel')
        
        if self.user_id.id>0 and self.user_id.slack_member_id!=False and self.user_id.slack_shipping_expedition_incidence==True:
            channel = self.user_id.slack_member_id                         
        
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'as_user': True,
            'channel': channel                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)        
    
    @api.one        
    def action_error_update_state_expedition(self, res):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            
        attachments = [
            {                    
                "title": 'Error al actualizar el estado de la expedicion',
                "text": res['error'],                         
                "color": "#ff0000",                                             
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
                        "title": "Expedicion",
                        "value": self.code,
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
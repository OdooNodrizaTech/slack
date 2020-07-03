# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.one    
    def action_error_create_shipping_expedition_message_slack(self, res):
        res_return = super(StockPicking, self).action_error_create_shipping_expedition_message_slack(res)
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    
        attachments = [
            {                    
                "title": 'Error al crear la expedicion',
                "text": res['error'],                        
                "color": "#ff0000",                                             
                "fallback": "Ver albaran "+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=stock.picking",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver albaran",
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=stock.picking"
                    }
                ],
                "fields": [
                    {
                        "title": "Albaran",
                        "value": self.name,
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
    
    @api.one    
    def action_error_edit_shipping_expedition_message_slack(self, res):
        res_return = super(StockPicking, self).action_error_edit_shipping_expedition_message_slack(res)
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            
        attachments = [
            {                    
                "title": 'Error al editar la expedicion',
                "text": res['error'],                         
                "color": "#ff0000",                                            
                "footer": str(record.author_id.name), 
                "fallback": "Ver albaran "+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=stock.picking",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver albaran",
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=stock.picking"
                    }
                ],
                "fields": [
                    {
                        "title": "Albaran",
                        "value": self.name,
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
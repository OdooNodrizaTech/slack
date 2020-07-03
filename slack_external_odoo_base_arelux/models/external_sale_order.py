# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class ExternalSaleOrder(models.Model):
    _inherit = 'external.sale.order'
        
    @api.one    
    def action_sale_order_done_error_partner_id_without_vat(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #attachments                        
        attachments = [
            {                    
                "title": 'Error al crear el external.sale.order',
                "text": 'No se puede confirmar el pedido porque el cliente NO tiene CIF',                        
                "color": "#ff0000",                                             
                "fallback": "Ver pedido "+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=external.sale.order",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver pedido",
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=external.sale.order"
                    }
                ],
                "fields": [
                    {
                        "title": "Source",
                        "value": self.external_source_id.name,
                        'short': True,
                    },                    
                    {
                        "title": "External Id",
                        "value": self.external_id,
                        'short': True,
                    },                    
                ],                    
            }
        ]        
        #slack_message_vals
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'as_user': True,
            'channel': str(self.env['ir.config_parameter'].sudo().get_param('slack_arelux_log_channel'))                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
    @api.one    
    def action_sale_order_done_error_external_shipping_address_id_without_country_id(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #attachments                        
        attachments = [
            {                    
                "title": 'Error al crear el external.sale.order',
                "text": 'No se puede confirmar el pedido porque la direccion de envio del cliente NO tiene PAIS mapeado',                        
                "color": "#ff0000",                                             
                "fallback": "Ver pedido "+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=external.sale.order",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver pedido",
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=external.sale.order"
                    }
                ],
                "fields": [
                    {
                        "title": "Source",
                        "value": self.external_source_id.name,
                        'short': True,
                    },                    
                    {
                        "title": "External Id",
                        "value": self.external_id,
                        'short': True,
                    },                    
                ],                    
            }
        ]        
        #slack_message_vals
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'as_user': True,
            'channel': str(self.env['ir.config_parameter'].sudo().get_param('slack_arelux_log_channel'))                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
    @api.one    
    def action_sale_order_done_error_external_shipping_address_id_without_country_state_id(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #attachments                        
        attachments = [
            {                    
                "title": 'Error al crear el external.sale.order',
                "text": 'No se puede confirmar el pedido porque la direccion de envio del cliente NO tiene PROVINCIA mapeada',                        
                "color": "#ff0000",                                             
                "fallback": "Ver pedido "+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=external.sale.order",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver pedido",
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=external.sale.order"
                    }
                ],
                "fields": [
                    {
                        "title": "Source",
                        "value": self.external_source_id.name,
                        'short': True,
                    },                    
                    {
                        "title": "External Id",
                        "value": self.external_id,
                        'short': True,
                    },                    
                ],                    
            }
        ]        
        #slack_message_vals
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'as_user': True,
            'channel': str(self.env['ir.config_parameter'].sudo().get_param('slack_arelux_log_channel'))                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)                    
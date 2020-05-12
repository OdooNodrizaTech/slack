# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from odoo import api, models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'    
    
    @api.one    
    def action_confirm_create_message_slack(self):
        attachments = self.action_confirm_create_message_slack_pre()[0]
        #channel        
        if self.ar_qt_activity_type=='todocesped':
            channel = self.env['ir.config_parameter'].sudo().get_param('slack_sale_order_confirm_todocesped')
        else:
            channel = self.env['ir.config_parameter'].sudo().get_param('slack_sale_order_confirm_arelux')         
        #vals                    
        slack_message_vals = {
            'attachments': attachments,
            'model': 'sale.order',
            'res_id': self.id,
            'channel': channel,                                                         
        }
        _logger.info(slack_message_vals)                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
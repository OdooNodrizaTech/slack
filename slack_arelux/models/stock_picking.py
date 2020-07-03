# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.one    
    def action_send_account_invoice_out_refund(self):
        return_object = super(StockPicking, self).action_send_account_invoice_out_refund()
        #slack
        self.action_send_account_invoice_out_refund_create_message_slack()
        #return
        return return_object
    
    @api.one    
    def action_send_account_invoice_out_refund_create_message_slack(self):
        if self.out_refund_invoice_id.id>0:
            web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                            
            attachments = [
                {                    
                    "title": 'Se ha creado la factura rectificativa automaticamente',
                    "text": self.out_refund_invoice_id.number,                        
                    "color": "#36a64f",                                             
                    "fallback": "Ver factura "+str(self.out_refund_invoice_id.number)+' '+str(web_base_url)+"/web?#id="+str(self.out_refund_invoice_id.id)+"&view_type=form&model=account.invoice",                                    
                    "actions": [
                        {
                            "type": "button",
                            "text": "Ver factura "+str(self.out_refund_invoice_id.number),
                            "url": str(web_base_url)+"/web?#id="+str(self.out_refund_invoice_id.id)+"&view_type=form&model=account.invoice"
                        }
                    ],
                    "fields": [                    
                        {
                            "title": "Cliente",
                            "value": self.out_refund_invoice_id.partner_id.name,
                            'short': True,
                        },
                        {
                            "title": "Origen",
                            "value": self.out_refund_invoice_id.origin,
                            'short': True,
                        }
                    ],                    
                }
            ]            
            
            slack_message_vals = {
                'attachments': attachments,
                'model': 'account.invoice',
                'res_id': self.out_refund_invoice_id.id,
                'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_contabilidad_channel'),                                                         
            }                        
            slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)                                
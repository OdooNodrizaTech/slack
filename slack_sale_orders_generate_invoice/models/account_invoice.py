# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one 
    def action_auto_open(self):
        return_item = super(AccountInvoice, self).action_auto_open()
        #action_send_account_invoice_create_message_slack
        self.action_send_account_invoice_create_message_slack()        
        #return
        return return_item
    
    @api.one    
    def action_send_account_invoice_create_message_slack(self):        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                        
        attachments = [
            {                    
                "title": 'Se ha creado la factura automaticamente',
                "text": self.number,                        
                "color": "#36a64f",                                             
                "fallback": "Ver factura "+str(self.number)+' '+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=account.invoice",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver factura "+str(self.number),
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=account.invoice"
                    }
                ],
                "fields": [                    
                    {
                        "title": "Cliente",
                        "value": self.partner_id.name,
                        'short': True,
                    },
                    {
                        "title": "Pedido",
                        "value": self.origin,
                        'short': True,
                    }
                ],                    
            }
        ]            
        
        slack_message_vals = {
            'attachments': attachments,
            'model': 'account.invoice',
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_contabilidad_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)                                
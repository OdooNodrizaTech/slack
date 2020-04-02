# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime
import decimal

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one 
    def account_invoice_auto_send_mail_item_real(self, mail_template_id, author_id):
        return_item = super(AccountInvoice, self).account_invoice_auto_send_mail_item_real(mail_template_id, author_id)
        #action_custom_send_mail_slack
        self.action_custom_send_mail_slack()        
        #return
        return return_item
    
    @api.one    
    def action_custom_send_mail_slack(self):
        res = super(AccountInvoice, self).action_custom_send_mail_slack()
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        attachments = [
            {                    
                "title": 'Se ha enviado por email la factura automaticamente',
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
                    }                    
                ],                    
            }
        ]        
        
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_contabilidad_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
        return res                                
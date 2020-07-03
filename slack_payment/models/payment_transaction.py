# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, tools

import logging
_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def action_payment_transaction_done_error(self, error):
        attachments = [
            {                    
                "title": 'Incidencia en Transaccion',
                "text": str(error['error']),                        
                "color": "#ff0000",                
                "fields": [
                    {
                        "title": "Referencia",
                        "value": str(error['reference']),
                        'short': True,
                    },                    
                    {
                        "title": "Entidad",
                        "value": str(error['acquirer_id_name']),
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
            'channel': str(self.env['ir.config_parameter'].sudo().get_param('slack_log_channel'))                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
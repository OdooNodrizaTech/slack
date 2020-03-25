# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.one    
    def action_send_cesce_risk_classification_error_message_slack(self, vals):
        res = super(ResPartner, self).action_send_cesce_risk_classification_error_message_slack(vals)
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                        
        attachments = [
            {                    
                "title": 'Error Cesce Clasificacion Riesgo',
                "text": vals['error'],                        
                "color": "#ff0000",                                             
                "fallback": "Ver contacto "+str(self.name)+' '+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=res.partner",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver contacto "+str(self.name),
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=res.partner"
                    }
                ],
                "fields": [                    
                    {
                        "title": "Contacto",
                        "value": self.name,
                        'short': True,
                    },
                    {
                        "title": "Importe solicitado",
                        "value": vals['importe_solicitado'],
                        'short': True,
                    }
                ],                    
            }
        ]            
        
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_cesce_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
        return res
        
    @api.one    
    def action_send_cesce_risk_classification_message_slack(self, vals):
        res = super(ResPartner, self).action_send_cesce_risk_classification_message_slack(vals)
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                        
        attachments = [
            {                    
                "title": 'Clasificacion Riesgo Concedida',
                "text": self.name,                        
                "color": "#36a64f",                                             
                "fallback": "Ver contacto "+str(self.name)+' '+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=res.partner",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver contacto "+str(self.name),
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=res.partner"
                    }
                ],
                "fields": [                    
                    {
                        "title": "Importe solicitado",
                        "value": vals['importe_solicitado'],
                        'short': True,
                    },
                    {
                        "title": "Importe concedido",
                        "value": vals['importe_concedido'],
                        'short': True,
                    }
                ],                    
            }
        ]            
        
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_cesce_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
        return res
        
    @api.one    
    def action_send_cesce_risk_classification_update_message_slack(self, vals):
        res = super(ResPartner, self).action_send_cesce_risk_classification_message_slack(vals)
        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                        
        attachments = [
            {                    
                "title": 'Clasificacion Riesgo Actualizada',
                "text": self.name,                        
                "color": "#36a64f",                                             
                "fallback": "Ver contacto "+str(self.name)+' '+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=res.partner",                                    
                "actions": [
                    {
                        "type": "button",
                        "text": "Ver contacto "+str(self.name),
                        "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=res.partner"
                    }
                ],
                "fields": [                    
                    {
                        "title": "Estado",
                        "value": vals['cesce_risk_state'],
                        'short': True,
                    },
                    {
                        "title": "Importe concedido",
                        "value": vals['importe_concedido'],
                        'short': True,
                    },
                    {
                        "title": "Fecha efecto",
                        "value": vals['fecha_efecto'],
                        'short': True,
                    },
                    {
                        "title": "Fecha anulacion",
                        "value": vals['fecha_anulacion'],
                        'short': True,
                    }
                ],                    
            }
        ]            
        
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_cesce_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
        
        return res
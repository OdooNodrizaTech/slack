# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.one
    def write(self, vals):
        #need_slack
        credit_limit_old = self.credit_limit
        if 'cesce_risk_state' in vals:            
            cesce_risk_state_old = self.cesce_risk_state
        #super                                                               
        return_object = super(ResPartner, self).write(vals)
        #need_slack
        if 'cesce_risk_state' in vals:
            credit_limit = self.credit_limit
            cesce_risk_state = self.cesce_risk_state
            #1er classification_error
            first_classification_error = False
            if cesce_risk_state=='classification_error' and cesce_risk_state_old!=cesce_risk_state:
                first_classification_error = True
                self.action_send_cesce_risk_classification_error_message_slack()
            #1er classification_ok
            first_classification_ok = False
            if cesce_risk_state=='classification_ok' and cesce_risk_state_old!=cesce_risk_state:
                first_classification_ok = True
                self.action_send_cesce_risk_classification_message_slack()
            #credit_limit change
            if first_classification_ok==False and first_classification_error==False:
                if credit_limit_old!=credit_limit:
                    self.action_send_cesce_risk_classification_update_message_slack()
        #return
        return return_object
    
    @api.one    
    def action_send_cesce_risk_classification_error_message_slack(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                        
        attachments = [
            {                    
                "title": 'Error Cesce Clasificacion Riesgo',
                "text": self.cesce_error,                        
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
                        "value": self.cesce_amount_requested,
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
        
    @api.one    
    def action_send_cesce_risk_classification_message_slack(self):
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
                        "value": self.cesce_amount_requested,
                        'short': True,
                    },
                    {
                        "title": "Importe concedido",
                        "value": self.credit_limit,
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
        
    @api.one    
    def action_send_cesce_risk_classification_update_message_slack(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #define
        fecha_efecto = ''
        fecha_anulacion = ''
        #cesce_risk_classification_ids
        cesce_risk_classification_ids = self.env['cesce.risk.classification'].sudo().search(
            [
                ('partner_id', '=', self.id)
            ], order="fecha_efecto desc", limit=1
        )
        if len(cesce_risk_classification_ids)>0:
            cesce_risk_classification_id = cesce_risk_classification_ids[0]
            fecha_efecto = cesce_risk_classification_id.fecha_efecto
            fecha_anulacion = cesce_risk_classification_id.fecha_anulacio        
        #attachments                                                        
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
                        "value": self.cesce_risk_state,
                        'short': True,
                    },
                    {
                        "title": "Importe concedido",
                        "value": self.credit_limit,
                        'short': True,
                    },
                    {
                        "title": "Fecha efecto",
                        "value": fecha_efecto,
                        'short': True,
                    },
                    {
                        "title": "Fecha anulacion",
                        "value": fecha_anulacion,
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
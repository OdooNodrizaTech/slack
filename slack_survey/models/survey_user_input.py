# -*- coding: utf-8 -*-
from openerp import _, api, exceptions, fields, models
from openerp.http import request
from dateutil.relativedelta import relativedelta
from datetime import datetime

import pytz

import logging
_logger = logging.getLogger(__name__)

class SurveyUserinput(models.Model):
    _inherit = 'survey.user_input'
    
    @api.model
    def create(self, values):
        return_object = super(SurveyUserinput, self).create(values)
        #action
        self.action_send_survey_mail_message_slack()
        #return_object
        return return_object
        
    @api.one    
    def action_send_survey_mail_message_slack(self):
        if self.type=='link':
            attachments = [
                {                    
                    "title": 'Se ha enviado por email la encuesta automaticamente',
                    "text": self.survey_id.title,                        
                    "color": "#36a64f",
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
                'model': 'survey.user_input',
                'res_id': self.id,
                'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_calidad_channel'),                                                         
            }                        
            slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)                                                                      
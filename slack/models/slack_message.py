# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
#from slackclient import SlackClient
import slack

import logging
_logger = logging.getLogger(__name__)

class SlackMessage(models.Model):
    _name = 'slack.message'
    _description = 'Slack Message'
    
    @api.model
    def create(self, values):        
        channel = self.env['ir.config_parameter'].sudo().get_param('slack_log_channel')
        api_token = tools.config.get('slack_bot_user_oauth_access_token')
        if api_token!=None:
            #api_token
            if 'api_token' in values:
                api_token = values['api_token']
            #default
            msg = ''
            attachments = []
            #msg
            if 'msg' in values:
                msg = values['msg']        
            #attachments
            if 'attachments' in values:
                attachments = values['attachments']
            #channel            
            if 'channel' in values:
                channel = values['channel']                    
            #SlackClient
            sc = slack.WebClient(api_token)
            #sc = SlackClient(api_token)
            result = sc.api_call(
                "chat.postMessage", 
                channel=channel, 
                text=msg, 
                attachments=attachments, 
                username='Odoo'
            )
            if 'error' in result:
                _logger.info({
                    'channel': channel,
                    'error': result['error'] 
                })
                                                
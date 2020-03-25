# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from slackclient import SlackClient
import threading

import logging
_logger = logging.getLogger(__name__)

class SlackMessage(models.Model):
    _name = 'slack.message'
    _description = 'Slack Message'
    
    @api.model
    def create(self, values):        
        channel = self.env['ir.config_parameter'].sudo().get_param('slack_oniad_log_channel')
        api_token = tools.config.get('slack_bot_user_oauth_access_token')
        
        msg = ''
        attachments = []
        
        if 'msg' in values:
            msg = values['msg']        
        
        if 'attachments' in values:
            attachments = values['attachments']
            
        if 'channel' in values:
            channel = values['channel']                                                        
                    
        #test
        thcall = threading.Thread(target=self.send_slack_message, args=(api_token, channel, msg, attachments))
        thcall.start()
        
    def send_slack_message(self, token, channel, message, attachments):
        sc = SlackClient(token)
        sc.api_call(
            "chat.postMessage", channel=channel, text=message, attachments=attachments, username='Odoo'
        )
        return {}                                        
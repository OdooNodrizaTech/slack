# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class GitRepository(models.Model):
    _inherit = 'git.repository'
    
    @api.one
    def action_clone_real(self, odoo_reboot=False, git_repository_log_id=0):
        return_action = super(GitRepository, self).action_clone_real(odoo_reboot, git_repository_log_id)
        #slack
        self.action_send_git_message_slack(odoo_reboot)
        #return
        return return_action
    
    @api.one    
    def action_send_git_message_slack(self, odoo_reboot):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                                        
        attachments = [
            {                    
                "title": 'Odoo Git Repository '+str(self.name),
                "text": self.url,                        
                "color": "#ff0000",
                "fields": [                    
                    {
                        "title": "Autor",
                        "value": self.git_author_id.name,
                        'short': True,
                    },
                    {
                        "title": "Odoo Reboot",
                        "value": odoo_reboot,
                        'short': True,
                    }
                ],                    
            }
        ]            
        
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_channel')                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)
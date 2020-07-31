# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.one
    def generate_auto_starred_slack(self, user_id):
        if user_id and user_id.slack_member_id and user_id.slack_mail_message:
            web_base_url = self.env[
                'ir.config_parameter'
            ].sudo().get_param('web.base.url')
            url_item = '%s/web?#id=%s&view_type=form&model=%s' % (
                web_base_url,
                self.res_id,
                self.model
            )
            if self.record_name:
                attachments = [
                    {
                        "title": _('New message'),
                        "text": str(self.record_name.encode('utf-8')),
                        "color": "#36a64f",
                        "footer": str(self.author_id.name.encode('utf-8')),
                        "fallback": _("View message %s  %s") % (
                            self.record_name.encode('utf-8'),
                            url_item
                        ),
                        "actions": [
                            {
                                "type": "button",
                                "text": _("View message %s")
                                        % self.record_name.encode('utf-8'),
                                "url": url_item
                            }
                        ]
                    }
                ]
                vals = {
                    'attachments': attachments,
                    'model': self._inherit,
                    'res_id': self.id,
                    'channel': user_id.slack_member_id
                }
                self.env['slack.message'].sudo().create(vals)

    @api.one
    def generate_notice_message_without_auto_starred_user_slack(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=%s' % (
            web_base_url,
            self.res_id,
            self.model
        )
        if self.record_name:
            attachments = [
                {
                    "title": 'Nuevo mensaje (Sin aviso a ningun comercial)',
                    "text": str(self.record_name.encode('utf-8')),
                    "color": "#ff0000",
                    "footer": str(self.author_id.name),
                    "fallback": _('View message %s %s') % (
                        self.record_name.encode('utf-8'),
                        url_item
                    ),
                    "actions": [
                        {
                            "type": "button",
                            "text": _('View message %s')
                                    % self.record_name.encode('utf-8'),
                            "url": url_item
                        }
                    ]
                }
            ]
            vals = {
                'attachments': attachments,
                'model': self._inherit,
                'res_id': self.id,
                'channel': self.env['ir.config_parameter'].sudo().get_param(
                    'slack_log_channel'
                ),
            }
            self.env['slack.message'].sudo().create(vals)

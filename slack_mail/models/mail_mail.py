# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def _postprocess_sent_message(self,
                                  success_pids,
                                  failure_reason=False,
                                  failure_type=None
                                  ):
        res = super(MailMail, self)._postprocess_sent_message(
            success_pids,
            failure_reason,
            failure_type
        )
        if failure_reason:
            for item in self:
                if item.state == 'exception':
                    attachments = [
                        {
                            "title": _('An error occurred while sending the email'),
                            "text": item.subject,
                            "color": "#ff0000",
                            "fields": [
                                {
                                    "title": _("Failure _reason"),
                                    "value": item.failure_reason,
                                    'short': True,
                                },
                                {
                                    "title": _("Email from"),
                                    "value": item.email_from,
                                    'short': True,
                                },
                                {
                                    "title": item.model,
                                    "value": item.res_id,
                                    'short': True,
                                },
                            ],
                        }
                    ]
                    vals = {
                        'attachments': attachments,
                        'model': self._inherit,
                        'res_id': item.id,
                    }
                    self.env['slack.message'].sudo().create(vals)
        # return
        return res

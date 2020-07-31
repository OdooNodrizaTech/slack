# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class SurveyUserinput(models.Model):
    _inherit = 'survey.user_input'

    @api.model
    def create(self, values):
        return_object = super(SurveyUserinput, self).create(values)
        # action
        self.action_send_survey_mail_message_slack()
        # return_object
        return return_object

    @api.multi
    def action_send_survey_mail_message_slack(self):
        for item in self:
            if item.type == 'link':
                attachments = [
                    {
                        "title": _('The survey has been automatically sent by email'),
                        "text": item.survey_id.title,
                        "color": "#36a64f",
                        "fields": [
                            {
                                "title": _("Customer"),
                                "value": item.partner_id.name,
                                'short': True,
                            }
                        ],
                    }
                ]
                vals = {
                    'attachments': attachments,
                    'model': 'survey.user_input',
                    'res_id': item.id,
                    'channel': self.env['ir.config_parameter'].sudo().get_param(
                        'slack_log_calidad_channel'
                    ),
                }
                self.env['slack.message'].sudo().create(vals)

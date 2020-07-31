# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def action_payment_transaction_done_error(self, error):
        attachments = [
            {
                "title": _('Incidence in payment transaction'),
                "text": str(error['error']),
                "color": "#ff0000",
                "fields": [
                    {
                        "title": _("Reference"),
                        "value": str(error['reference']),
                        'short': True,
                    },
                    {
                        "title": _("Acquirer"),
                        "value": str(error['acquirer_id_name']),
                        'short': True,
                    },
                ],
            }
        ]
        # vals
        vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'as_user': True,
            'channel': self.env['ir.config_parameter'].sudo().get_param(
                'slack_log_channel'
            )
        }
        self.env['slack.message'].sudo().create(vals)

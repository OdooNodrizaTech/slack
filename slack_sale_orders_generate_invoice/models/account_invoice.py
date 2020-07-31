# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from odoo import api, models, _
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_auto_open(self):
        return_item = super(AccountInvoice, self).action_auto_open()
        # action_send_account_invoice_create_message_slack
        for item in self:
            item.action_send_account_invoice_create_message_slack()
        # return
        return return_item
    
    @api.multi
    def action_send_account_invoice_create_message_slack(self):
        self.ensure_one()
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=account.invoice' % (
            web_base_url,
            self.id
        )
        attachments = [
            {
                "title": _('Invoice has been created automatically'),
                "text": self.number,
                "color": "#36a64f",
                "fallback": "View invoice %s %s" % (
                    self.number,
                    url_item
                ),
                "actions": [
                    {
                        "type": "button",
                        "text": _("View invoice %s") % self.number,
                        "url": url_item
                    }
                ],
                "fields": [
                    {
                        "title": _("Customer"),
                        "value": self.partner_id.name,
                        'short': True,
                    },
                    {
                        "title": _("Origin"),
                        "value": self.origin,
                        'short': True,
                    }
                ],
            }
        ]
        vals = {
            'attachments': attachments,
            'model': 'account.invoice',
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param(
                'slack_log_contabilidad_channel'
            ),
        }                        
        self.env['slack.message'].sudo().create(vals)

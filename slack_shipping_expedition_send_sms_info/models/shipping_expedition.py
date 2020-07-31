# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _


class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    @api.multi
    def action_send_sms_info_real(self):
        return_item = super(ShippingExpedition, self).action_send_sms_info_real()
        # action_send_sms_info_expedition_message_slack
        for item in self:
            item.action_send_sms_info_expedition_message_slack()
        # return
        return return_item

    @api.multi
    def action_send_sms_info_expedition_message_slack(self):
        self.ensure_one()
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=shipping.expedition' % (
            web_base_url,
            self.id
        )
        attachments = [
            {
                "title": _('The information of the expedition has been sent by sms'),
                "text": self.code,
                "color": "#36a64f",
                "fallback": _("View expedition %s") % url_item,
                "actions": [
                    {
                        "type": "button",
                        "text": _("View expedition"),
                        "url": url_item
                    }
                ],
                "fields": [
                    {
                        "title": _("Picking"),
                        "value": self.picking_id.name,
                        'short': True,
                    },
                    {
                        "title": _("Carrier"),
                        "value": self.carrier_type.title(),
                        'short': True,
                    },
                ],
            }
        ]
        vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param(
                'slack_log_almacen_channel'
            ),
        }
        self.env['slack.message'].sudo().create(vals)

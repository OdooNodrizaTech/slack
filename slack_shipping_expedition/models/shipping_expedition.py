# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _


class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    @api.multi
    def write(self, vals):
        # state_old
        state_old = None
        if 'state' in vals:
            state_old = self.state
        # write
        return_write = super(ShippingExpedition, self).write(vals)
        # operations
        if 'state' in vals:
            if self.state == 'incidence' and state_old != self.state:
                self.action_incidence_expedition_message_slack()
        # return
        return return_write

    @api.multi
    def action_incidence_expedition_message_slack(self):
        self.ensure_one()
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=shipping.expedition' % (
            web_base_url,
            self.id
        )
        attachments = [
            {
                "title": _('Incidence in expedition'),
                "text": self.observations,
                "color": "#ff0000",
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
                        "title": _("Expedition"),
                        "value": self.code,
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
        channel = self.env['ir.config_parameter'].sudo().get_param(
            'slack_log_almacen_channel'
        )
        if self.user_id \
                and self.user_id.slack_member_id \
                and self.user_id.slack_shipping_expedition_incidence:
            channel = self.user_id.slack_member_id

        vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'as_user': True,
            'channel': channel
        }
        self.env['slack.message'].sudo().create(vals)

    @api.multi
    def action_error_update_state_expedition(self, res):
        self.ensure_one()
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=shipping.expedition' % (
            web_base_url,
            self.id
        )
        attachments = [
            {
                "title": 'Error al actualizar el estado de la expedicion',
                "text": res['error'],
                "color": "#ff0000",
                "fallback": _("Ver expedicion %s") % url_item,
                "actions": [
                    {
                        "type": "button",
                        "text": _("Ver expedicion"),
                        "url": url_item
                    }
                ],
                "fields": [
                    {
                        "title": _("Expedicion"),
                        "value": self.code,
                        'short': True,
                    },
                    {
                        "title": _("Transportista"),
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

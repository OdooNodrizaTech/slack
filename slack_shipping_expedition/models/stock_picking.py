# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one    
    def action_error_create_shipping_expedition_message_slack(self, res):        
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=stock.picking' % (
            web_base_url,
            self.id
        )
        attachments = [
            {                    
                "title": _('Error creating the expedition'),
                "text": res['error'],                        
                "color": "#ff0000",
                "fallback": _("View picking %s") % url_item,
                "actions": [
                    {
                        "type": "button",
                        "text": _("View picking"),
                        "url": url_item
                    }
                ],
                "fields": [
                    {
                        "title": _("Picking"),
                        "value": self.name,
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

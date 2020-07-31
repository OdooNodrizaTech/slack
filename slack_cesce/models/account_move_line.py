# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.one
    def write(self, vals):
        # need_slack
        if 'cesce_sale_state' in vals:            
            cesce_sale_state_old = self.cesce_sale_state
        # super
        return_object = super(AccountMoveLine, self).write(vals)
        # need_slack
        if 'cesce_sale_state' in vals:
            cesce_sale_state = self.cesce_sale_state
            if cesce_sale_state == 'sale_error' \
                    and cesce_sale_state != cesce_sale_state_old:
                self.action_send_cesce_sale_error_message_slack()
        # return
        return return_object

    @api.one    
    def action_send_cesce_sale_error_message_slack(self, vals):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_item = '%s/web?#id=%s&view_type=form&model=account.move.line' % (
            web_base_url,
            self.id
        )
        attachments = [
            {                    
                "title": _('Error Cesce Ventas'),
                "text": self.cesce_error,                        
                "color": "#ff0000",
                "fallback": _("View account move line %s %s") % (
                    self.name,
                    url_item
                ),
                "actions": [
                    {
                        "type": "button",
                        "text": _('View account move line %s' % self.name),
                        "url": url_item
                    }
                ]                    
            }
        ]
        slack_message_vals = {
            'attachments': attachments,
            'model': self._inherit,
            'res_id': self.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param(
                'slack_cesce_channel'
            ),
        }                        
        self.env['slack.message'].sudo().create(slack_message_vals)

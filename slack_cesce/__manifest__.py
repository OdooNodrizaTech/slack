# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Slack Cesce",
    "version": "12.0.1.0.0",
    "author": "Odoo Nodriza Tech (ONT), "
              "Odoo Community Association (OCA)",
    "website": "https://nodrizatech.com/",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "slack",
        "cesce"  # https://github.com/OdooNodrizaTech/tools
    ],
    "data": [
        "data/slack_data.xml",
    ],
    "installable": True
}

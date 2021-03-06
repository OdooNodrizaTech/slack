# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Slack SQS Dead Letter",
    "version": "12.0.1.0.0",
    "author": "Odoo Nodriza Tech (ONT), "
              "Odoo Community Association (OCA)",
    "website": "https://nodrizatech.com/",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": [
        "base",
        "slack"
    ],
    "external_dependencies": {
        "python": ["boto3"],
    },
    "data": [
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
    ],
    "installable": True
}

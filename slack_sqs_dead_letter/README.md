El módulo se basa en el addon de Slack y consiste en consultar los mensajes de las SQS definidas y envia un mensaje a Slack por cada mensaje que encuentra

Los nombres de las SQS deberán estar separados por ,
Lo ideal es que no exista ningún mensaje en esos SQS porque sería un error en el proceso previa que ha provocado que acabe ahí

### odoo.conf
- aws_access_key_id=xxxx
- aws_secret_key_id=xxxxx
- aws_region_name=eu-west-1

## Parámetros de configuración
- slack_log_sqs_dead_letter
- sqs_dead_letter_urls

### Cron Slack SQS Dead Letter

Frecuencia: 1 vez al día

Descripción: Consulta los mensajes de los SQS definidos y por cada uno envía un mensaje al canal de Slack previamente definido.

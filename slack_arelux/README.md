El módulo contiene el desarrollo que permite realizar toda la integración respecto a Slack específicas para Arelux tomando como referencia el addon de slack.

 
## Parámetros de configuración
```
slack_arelux_report_channel
slack_arelux_reporte_ranking_semanal
``` 

## Cron

### Slack Channel Daily Report
Frecuencia: 1 vez al día

Limitaciones: Existen unas limitaciones internas que hacen que SOLO se realice de Lunes-Sabádo

Descripción: Envía por Slack al canal establecido el reporte diario de ventas de Profesionales y de Particulares


## Reporte de ventas diario

Todos los datos obtenidos del reporte de ventas se generarán hoy (Miércoles): de los datos de ayer (Martes) comparándolos con ante-ayer (Lunes)

### Profesionales

- [Todocesped] Facturación del día: 0€ (con colores)
- [Arelux] Facturación del día: 0€ (con colores)
- [Todocesped] Numero de pedidos del día: 1 (con colores)
- [Arelux] Numero de pedidos del día: 1 (con colores)
- [Todocesped] Cartera de clientes profesionales activos: 1
- [Arelux] Cartera de clientes profesionales activos:
- [Todocesped] Numero de albaranes hechos:1 (con colores)
- [Arelux] Numero de albaranes hechos:1 (con colores)
- [Todocesped] Cartera de clientes profesionales sin compra: 1
- [Arelux] Cartera de clientes profesionales sin compra: 1
- [Todocesped] Clientes profesionales nuevos metidos al sistema:1 (con colores)
- [Arelux] Clientes profesionales nuevos metidos al sistema:1 (con colores)
- [Todocesped] Clientes profesionales con primera compra:1 (con colores)
- [Arelux] Clientes profesionales con primera compra:1 (con colores)

### Particulares

- [Todocesped] Facturación del día: 0€ (con colores)
- [Arelux] Facturacion del día: 0€ (con colores)
- [Todocesped] Numero de pedidos del día: 1 (con colores)
- [Arelux] Numero de pedidos del día: 1 (con colores)
- [Todocesped] Numero de presupuestos del día enviados por email: 1 (con colores)
- [Arelux] Numero de presupuestos del día enviados por email (con colores)
- [Todocesped] Numero de albaranes hechos: 1 (con colores)
- [Arelux] Numero de albaranes hechos: 1 (con colores)
- [Todocesped] % de muestras sobre presupuestos: 0% (con colores)
- [Arelux] % de muestras sobre presupuestos: 0% (con colores)
- [Todocesped] % Presupuestos realizados contra asignados: 0% (con colores)
- [Arelux] % Presupuestos realizados contra asignados: 0% (con colores)
- [Todocesped] Flujos sin asignar (ayer): 0 (con colores)
- [Arelux] Flujos sin asignar (ayer): 0 (con colores)
- [Todocesped] Flujos sin asignar (últimos mes): 0 (con colores)
- [Arelux] Flujos sin asignar (últimos mes): 0 (con colores)

Cuando se especifica "con colores" indica que a cada dato en Slack acompañará un color "rojo" si el dato a empeorado respecto al día anterior, verde si ha mejorado, y sin color si el dato sacado no tiene datos a mostrar.

### Slack Reporte Ranking Semanal
Frecuencia: 1 vez a la semana

Descripción: Envía por Slack al canal establecido el ranking semanal TODOCESPED con la siguiente información: 

- Presupuestos enviados x comercial (excluyendo los automáticos). Que se contemplen los asignados y enviados (particular)
- Presupuestos aceptados x comercial (particular)
- UpSelling x comercial --> presupuestos aceptados en los que hay cepillo, cutter o perfume con precio superior a cero euros. (particular)
- Ventas totales por comercial ---> Nº de Pedidos + Base Imponible € (particular+profesional)

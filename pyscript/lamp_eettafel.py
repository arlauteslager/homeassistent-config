# /config/pyscript/eetkamertafel_licht.py
#
# Beweging of lamp-aan -> zet eetkamertafellamp op dagdeel-instellingen

from datetime import datetime, time

@state_trigger("binary_sensor.woonkamer4in1 == 'on' or light.lamp_eetkamertafel == 'on'")
def _run():
    t = datetime.now().time()

    if time(6, 0) <= t < time(16, 0):
        service.call("light", "turn_on", entity_id="light.lamp_eetkamertafel", brightness_pct=100, color_temp_kelvin=5000)
    elif time(16, 0) <= t < time(20, 0):
        service.call("light", "turn_on", entity_id="light.lamp_eetkamertafel", brightness_pct=50, color_temp_kelvin=2250)
    elif time(20, 0) <= t <= time(23, 59, 59):
        service.call("light", "turn_on", entity_id="light.lamp_eetkamertafel", brightness_pct=20, color_temp_kelvin=2100)

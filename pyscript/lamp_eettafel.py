# /config/pyscript/eetkamertafel_licht.py
#
# Omzetting van:
# Beweging → eetkamertafel-licht per dagdeel
#
# Triggers:
# - beweging: binary_sensor.woonkamer4in1 -> on
# - lamp zelf: light.lamp_eetkamertafel -> on
#
# Actie:
# - zet dezelfde lamp aan met instellingen afhankelijk van tijdvak
#
# Opmerking over "mode: restart":
# - YAML restart betekent: nieuwe trigger start opnieuw (oude run wordt afgebroken).
# - In dit script is er geen delay/sleep, dus "restart" maakt praktisch geen verschil.

from datetime import datetime, time

MOTION = "binary_sensor.woonkamer4in1"
LIGHT = "light.lamp_eetkamertafel"


def _set_light(brightness_pct: int, kelvin: int):
    service.call(
        "light",
        "turn_on",
        entity_id=LIGHT,
        brightness_pct=brightness_pct,
        color_temp_kelvin=kelvin,
    )


def _in_range(now_t: time, start: time, end: time) -> bool:
    return start <= now_t < end


@state_trigger(f"{MOTION} == 'on' or {LIGHT} == 'on'")
def beweging_eetkamertafel_per_dagdeel():
    now_t = datetime.now().time()

    if _in_range(now_t, time(6, 0), time(16, 0)):
        _set_light(100, 5000)
    elif _in_range(now_t, time(16, 0), time(20, 0)):
        _set_light(50, 2250)
    elif _in_range(now_t, time(20, 0), time(23, 59, 59)):
        _set_light(20, 2100)
    else:
        # default: niets doen
        return

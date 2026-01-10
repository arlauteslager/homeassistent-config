# /config/pyscript/lamp_voorkamer.py
#
# Regels:
# - NIET BEWOOND: in de avond 1 uur na zonsondergang t/m 22:40 lamp aan
# - BEWOOND:
#   - avond: vanaf zonsondergang t/m 22:40 aan als het NIET "echt donker" binnen is (lux >= 10),
#           uit zodra het "echt donker" is (lux < 10)
#   - ochtend: vanaf 07:00 t/m zonsopgang:
#       - aan wanneer beweging gedetecteerd
#       - uit 20 min na geen beweging
#
# Entities:
# - switch.stekker_lamp_voorkamer
# - binary_sensor.bewoond
# - sensor.woonkamer4in1_licht
# - binary_sensor.woonkamer4in1  (beweging)

from datetime import datetime, time

def _set(on):
    cur = state.get("switch.stekker_lamp_voorkamer")
    if on and cur != "on":
        service.call("switch", "turn_on", entity_id="switch.stekker_lamp_voorkamer")
    elif (not on) and cur != "off":
        service.call("switch", "turn_off", entity_id="switch.stekker_lamp_voorkamer")

def _apply(ctx=""):
    bewoond = state.get("binary_sensor.bewoond") == "on"
    motion = state.get("binary_sensor.woonkamer4in1") == "on"
    now = datetime.now()
    t = now.time()

    # hard cutoff altijd
    if t >= time(22, 40):
        _set(False)
        return

    # ochtend: 07:00 -> zonsopgang (zon onder horizon)
    morning = (t >= time(7, 0) and state.get("sun.sun") == "below_horizon")
    # avond: na zonsondergang (zon onder horizon)
    evening = (state.get("sun.sun") == "below_horizon")

    if not bewoond:
        # NIET BEWOOND: start exact op sunset+1h (via trigger), daarna aan tot cutoff
        # Overdag: uit
        if evening:
            _set(True)
        else:
            _set(False)
        return

    # BEWOOND
    if morning:
        # Ochtend: aan bij beweging; uit gaat via motion_off trigger met delay
        if motion:
            _set(True)
        return

    if evening:
        # Avond: aan zolang lux >= 10; uit zodra lux < 10
        try:
            lux = float(state.get("sensor.woonkamer4in1_licht"))
        except (TypeError, ValueError):
            lux = 9999.0
        _set(lux >= 10.0)
        return

    # Overdag: uit

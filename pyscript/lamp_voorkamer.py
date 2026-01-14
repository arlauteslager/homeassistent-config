# /config/pyscript/lamp_voorkamer.py
#
# Regels:
# - NIET BEWOOND: in de avond 1 uur na zonsondergang t/m 22:40 lamp aan
# - BEWOOND: lamp voorkamer volgt lamp_eetkamertafel (aan/uit)
# - Extra: bij beweging woonkamer4in1 (alleen bewoond) synchroniseren we direct
#
# Entities:
# - switch.stekker_lamp_voorkamer
# - binary_sensor.bewoond
# - light.lamp_eetkamertafel
# - binary_sensor.woonkamer4in1  (beweging)

from datetime import datetime, time

# Zet de voorkamerlamp alleen als de gewenste status afwijkt
def _set(on):
    cur = state.get("switch.stekker_lamp_voorkamer")
    if on and cur != "on":
        service.call("switch", "turn_on", entity_id="switch.stekker_lamp_voorkamer")
    elif (not on) and cur != "off":
        service.call("switch", "turn_off", entity_id="switch.stekker_lamp_voorkamer")

# Reageert op wisselen tussen bewoond / niet bewoond
@state_trigger("binary_sensor.bewoond == 'on' or binary_sensor.bewoond == 'off'")
def bewoond_change():
    if datetime.now().time() >= time(22, 40):
        _set(False)
    elif state.get("binary_sensor.bewoond") == "on":
        _set(state.get("light.lamp_eetkamertafel") == "on")
    else:
        _set(False)

# Houdt voorkamerlamp gelijk aan eetkamertafel als je daar schakelt
@state_trigger("light.lamp_eetkamertafel")
def eetkamertafel_any_change():
    if datetime.now().time() >= time(22, 40):
        _set(False)
    elif state.get("binary_sensor.bewoond") == "on":
        _set(state.get("light.lamp_eetkamertafel") == "on")

# Extra synchronisatie: bij beweging checken we opnieuw de eetkamertafel-lamp
@state_trigger("binary_sensor.woonkamer4in1 == 'on'")
def motion_sync():
    if datetime.now().time() >= time(22, 40):
        _set(False)
    elif state.get("binary_sensor.bewoond") == "on":
        _set(state.get("light.lamp_eetkamertafel") == "on")

# Niet bewoond: start avondverlichting exact 1 uur na zonsondergang
@state_trigger("binary_sensor.zon_onder == 'on'")
async def t_sunset_plus1():
    # vervangt alleen het tijdstip (sunset+1h)
    await task.sleep(3600)

    # rest is identiek aan je oude code
    if state.get("binary_sensor.bewoond") == "off" and datetime.now().time() < time(22, 40):
        _set(True)

# Altijd om 22:40 lamp uit (hard cutoff)
@time_trigger("cron(40 22 * * *)")
def t_cutoff():
    _set(False)

# Synchronisatie bij herstart van Home Assistant / Pyscript
@time_trigger("startup")
def t_startup():
    if datetime.now().time() >= time(22, 40):
        _set(False)
    elif state.get("binary_sensor.bewoond") == "on":
        _set(state.get("light.lamp_eetkamertafel") == "on")
    else:
        _set(False)

# /config/pyscript/lamp_voorkamer.py
#
# Regels:
# - NIET BEWOOND: aan als donker buiten én vóór 22:40
# - BEWOOND: aan als donker buiten én NIET donker binnen (lux >= 10)
# Triggers: bewoond/donker_buiten changes, elke 10 min als donker, 22:40

from datetime import datetime, time

def _lux():
    try:
        return float(state.get("sensor.woonkamer4in1_licht"))
    except (TypeError, ValueError):
        return 9999.0

def _set(desired_on: bool):
    cur = state.get("switch.stekker_lamp_voorkamer")
    if desired_on and cur != "on":
        service.call("switch", "turn_on", entity_id="switch.stekker_lamp_voorkamer")
    elif (not desired_on) and cur != "off":
        service.call("switch", "turn_off", entity_id="switch.stekker_lamp_voorkamer")

def _apply(ctx: str):
    bewoond = (state.get("binary_sensor.bewoond") == "on")
    donker_buiten = (state.get("binary_sensor.donker_buiten") == "on")
    t = datetime.now().time()
    lux = _lux()
    donker_binnen = lux < 10.0

    if not bewoond:
        desired_on = donker_buiten and (t < time(22, 40))
    else:
        desired_on = donker_buiten and (not donker_binnen)

    log.warning(
        "[lamp_voorkamer] %s | bewoond=%s | donker_buiten=%s | lux=%s | donker_binnen=%s | tijd=%s | desired_on=%s | current=%s",
        ctx,
        state.get("binary_sensor.bewoond"),
        state.get("binary_sensor.donker_buiten"),
        state.get("sensor.woonkamer4in1_licht"),
        donker_binnen,
        t.strftime("%H:%M:%S"),
        desired_on,
        state.get("switch.stekker_lamp_voorkamer"),
    )

    _set(desired_on)


@state_trigger("binary_sensor.bewoond == 'on' or binary_sensor.bewoond == 'off'")
def _bewoond():
    _apply("bewoond_change")

@state_trigger("binary_sensor.donker_buiten == 'on' or binary_sensor.donker_buiten == 'off'")
def _donker_buiten():
    _apply("donker_buiten_change")

@time_trigger("cron(*/10 * * * *)")
def _periodic():
    if state.get("binary_sensor.donker_buiten") == "on":
        _apply("periodic_dark")

@time_trigger("cron(40 22 * * *)")
def _cutoff():
    _apply("cutoff_2240")

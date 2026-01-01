# /config/pyscript/lamp_voorkamer.py
#
# Regels:
# - NIET BEWOOND: aan van donker_buiten -> 22:40
# - BEWOOND: aan van donker_buiten -> totdat het DONKER BINNEN is (woonkamer4in1 lux < drempel)
#
# Bij jou:
# - BEWOOND = bestaande template binary_sensor
# - DONKER_BUITEN = bestaande template binary_sensor
# - DONKER BINNEN = lux van woonkamer4in1 (deze versie)

from datetime import datetime, time

# =========================
# CONFIG: pas dit aan
# =========================

SWITCH = "switch.stekker_lamp_voorkamer"

BEWOOND = "binary_sensor.bewoond"              # <-- jouw bestaande template sensor
DONKER_BUITEN = "binary_sensor.donker_buiten"  # <-- jouw bestaande template sensor

# Vul hier je echte lux/illuminance sensor in:
WOONKAMER_LUX = "sensor.woonkamer4in1_licht"  # <-- PAS AAN indien nodig

# Drempel: onder deze luxwaarde vinden we het "donker binnen"
LUX_DREMPEL = 10.0

# Cut-off tijd als NIET BEWOOND
CUTOFF_NIET_BEWOOND = time(22, 40)


# =========================
# Helpers
# =========================

def is_on(entity_id: str) -> bool:
    return state.get(entity_id) == "on"


def now_time() -> time:
    return datetime.now().time()


def lux_value() -> float:
    """Lees lux als float; bij onbekend -> hoog getal zodat het niet 'donker' wordt."""
    try:
        return float(state.get(WOONKAMER_LUX))
    except (TypeError, ValueError):
        return 9999.0


def is_donker_binnen() -> bool:
    return lux_value() < LUX_DREMPEL


def set_switch(desired_on: bool):
    current = state.get(SWITCH)
    if desired_on and current != "on":
        service.call("switch", "turn_on", entity_id=SWITCH)
    elif (not desired_on) and current != "off":
        service.call("switch", "turn_off", entity_id=SWITCH)


def apply_rule():
    bewoond = is_on(BEWOOND)
    donker_buiten = is_on(DONKER_BUITEN)

    if not bewoond:
        # NIET BEWOOND: donker buiten -> 22:40
        desired_on = donker_buiten and (now_time() < CUTOFF_NIET_BEWOOND)
        set_switch(desired_on)
        return

    # BEWOOND: donker buiten -> totdat donker binnen is (lux onder drempel)
    desired_on = donker_buiten and (not is_donker_binnen())
    set_switch(desired_on)


# =========================
# Triggers
# =========================

@state_trigger(f"{BEWOOND} == 'on' or {BEWOOND} == 'off'")
def trig_bewoond_change():
    apply_rule()


@state_trigger(f"{DONKER_BUITEN} == 'on' or {DONKER_BUITEN} == 'off'")
def trig_donker_buiten_change():
    apply_rule()


@state_trigger(f"{WOONKAMER_LUX}")
def trig_lux_change():
    apply_rule()


# Vangnet specifiek voor 22:40 cut-off 
@time_trigger("cron(40 22 * * *)")
def trig_cutoff():
    apply_rule()


# Extra robuustheid: herbereken bij HA-start en bij start van de dag
@event_trigger("homeassistant_started")
def trig_ha_start(event_name, data, kwargs):
    apply_rule()


@time_trigger("cron(0 0 * * *)")
def trig_midnight():
    apply_rule()


@service
def lamp_voor_eval():
    """Handmatig herberekenen."""
    apply_rule()

# /config/pyscript/boiler_regeling.py
#
# Doel:
# Slimme boilerregeling op basis van:
# - teruglevering / import (P1-meter)
# - maximale dagelijkse opwarmtijd
# - bewoning (binary_sensor.bewoond)
#
# Gedrag:
# 1) Dagelijkse reset om 06:00 (timer + flags)
# 2) Boiler AAN bij voldoende teruglevering
# 3) Boiler UIT bij import (voor 16:00)
# 4) Boiler UIT + markeer verwarmd als timer klaar is
# 5) Geforceerde run om 16:00 (wo–zo) gedurende 15 min
#
# Deze versie:
# - gebruikt drempel-triggers (geen spam)
# - heeft guards voor BEWOOND
# - is robuust tegen rare states
#
# Logging:
# - Pyscript zelf logt standaard "has been triggered by ...".
#   Dat zet je uit/omlaag via configuration.yaml logger-instellingen.
# - In dit script staat optionele, rustige logging die alleen logt bij echte acties.
#   Zet DEBUG_LOG = True als je die wilt zien.

from datetime import datetime, time

# --------------------------------------------------
# Entities
# --------------------------------------------------
BOILER_SWITCH = "switch.boiler_stopcontact_1"
ALREADY_HEATED = "input_boolean.boiler_al_verwarmd"
HEAT_TIMER = "timer.boiler_opwarmtijd"
P1_POWER = "sensor.p1_meter_power"
BEWOOND_SENSOR = "binary_sensor.bewoond"

# --------------------------------------------------
# Instellingen
# --------------------------------------------------
EXPORT_ON_THRESHOLD_W = -1100     # teruglevering → boiler mag aan
IMPORT_OFF_THRESHOLD_W = 1200     # import → boiler uit
DAILY_TIMER_DURATION = "00:30:00"

FORCED_RUN_TIME = time(16, 0)
FORCED_RUN_MINUTES = 15

# --------------------------------------------------
# Logging (optioneel)
# --------------------------------------------------
DEBUG_LOG = False

def _dbg(msg: str):
    """Rustige debug logging (alleen als DEBUG_LOG True is)."""
    if DEBUG_LOG:
        log.info(msg)

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def _now_time() -> time:
    """Huidige tijd als datetime.time"""
    return datetime.now().time()


def _as_float(entity_id: str, default: float = 0.0) -> float:
    """
    Lees entity state veilig als float.
    Voorkomt crashes bij 'unknown' / 'unavailable'.
    """
    v = state.get(entity_id)
    if v in (None, "unknown", "unavailable"):
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _require_bewoond() -> bool:
    """True als huis als bewoond wordt beschouwd"""
    return state.get(BEWOOND_SENSOR) == "on"


def _switch_on(entity_id: str):
    # Log alleen als er echt een wijziging volgt (voorkomt ruis)
    if state.get(entity_id) != "on":
        _dbg(f"Boiler: switch ON ({entity_id})")
    service.call("switch", "turn_on", entity_id=entity_id)


def _switch_off(entity_id: str):
    if state.get(entity_id) != "off":
        _dbg(f"Boiler: switch OFF ({entity_id})")
    service.call("switch", "turn_off", entity_id=entity_id)


def _bool_on(entity_id: str):
    if state.get(entity_id) != "on":
        _dbg(f"Boiler: input_boolean ON ({entity_id})")
    service.call("input_boolean", "turn_on", entity_id=entity_id)


def _bool_off(entity_id: str):
    if state.get(entity_id) != "off":
        _dbg(f"Boiler: input_boolean OFF ({entity_id})")
    service.call("input_boolean", "turn_off", entity_id=entity_id)


def _timer_start(entity_id: str, duration: str = None):
    if duration:
        _dbg(f"Boiler: timer start ({entity_id}) duration={duration}")
        service.call("timer", "start", entity_id=entity_id, duration=duration)
    else:
        _dbg(f"Boiler: timer start ({entity_id})")
        service.call("timer", "start", entity_id=entity_id)


def _timer_pause(entity_id: str):
    _dbg(f"Boiler: timer pause ({entity_id})")
    service.call("timer", "pause", entity_id=entity_id)


# --------------------------------------------------
# 1) Dagelijkse reset om 06:00
# --------------------------------------------------
@time_trigger("cron(0 6 * * *)")
def boiler_timer_reset_dagelijks():
    """
    Reset aan het begin van de dag:
    - boiler uit
    - 'al verwarmd' uit
    - timer opnieuw op 30 min en pauzeren
    """
    _dbg("Boiler: dagelijkse reset 06:00")
    _switch_off(BOILER_SWITCH)
    task.sleep(2)

    _bool_off(ALREADY_HEATED)

    _timer_start(HEAT_TIMER, duration=DAILY_TIMER_DURATION)
    task.sleep(1)
    _timer_pause(HEAT_TIMER)


# --------------------------------------------------
# 2) Boiler AAN bij voldoende teruglevering
# --------------------------------------------------
@state_trigger(f"float({P1_POWER}) < {EXPORT_ON_THRESHOLD_W}")
def boiler_aan_bij_teruglevering():
    """
    Start de boiler als:
    - er voldoende wordt teruggeleverd
    - huis bewoond is
    - boiler nog niet eerder vandaag verwarmd heeft
    - boiler momenteel uit staat
    - timer gepauzeerd is
    """
    power = _as_float(P1_POWER)
    if power >= EXPORT_ON_THRESHOLD_W:
        return

    if not _require_bewoond():
        return
    if state.get(ALREADY_HEATED) != "off":
        return
    if state.get(BOILER_SWITCH) != "off":
        return

    timer_state = state.get(HEAT_TIMER)

    if timer_state == "paused":
        _dbg(f"Boiler: AAN bij teruglevering (P1={power:.0f}W), timer actief")
        _switch_on(BOILER_SWITCH)
        _timer_start(HEAT_TIMER)
        return

    if timer_state == "idle":
        _dbg(f"Boiler: timer al idle bij teruglevering (P1={power:.0f}W) -> markeer verwarmd")
        _bool_on(ALREADY_HEATED)
        return


# --------------------------------------------------
# 3) Boiler UIT bij import vóór 16:00
# --------------------------------------------------
@state_trigger(f"float({P1_POWER}) > {IMPORT_OFF_THRESHOLD_W}")
def boiler_uit_bij_import():
    """
    Zet de boiler uit als:
    - er netto import is boven drempel
    - het vóór 16:00 is
    - de boiler aan staat
    """
    power = _as_float(P1_POWER)
    if power <= IMPORT_OFF_THRESHOLD_W:
        return

    if state.get(BOILER_SWITCH) != "on":
        return
    if _now_time() >= FORCED_RUN_TIME:
        return

    timer_state = state.get(HEAT_TIMER)

    if timer_state == "idle":
        _dbg(f"Boiler: UIT bij import (P1={power:.0f}W), timer idle -> markeer verwarmd")
        _bool_on(ALREADY_HEATED)
    elif timer_state == "active":
        _dbg(f"Boiler: UIT bij import (P1={power:.0f}W), timer active -> pauzeer timer")
        _timer_pause(HEAT_TIMER)

    _switch_off(BOILER_SWITCH)


# --------------------------------------------------
# 4) Timer afgelopen → boiler uit + markeer verwarmd
# --------------------------------------------------
@event_trigger("timer.finished")
def boiler_timer_finished(event_name, data, kwargs):
    """
    Als de maximale dagelijkse opwarmtijd is bereikt:
    - markeer als verwarmd
    - zet boiler uit
    """
    if data.get("entity_id") != HEAT_TIMER:
        return

    _dbg("Boiler: timer finished -> markeer verwarmd + boiler uit")
    _bool_on(ALREADY_HEATED)
    _switch_off(BOILER_SWITCH)


# --------------------------------------------------
# 5) Geforceerde boiler-run om 16:00 (wo–zo)
# --------------------------------------------------
@time_trigger("cron(0 16 * * 3-7)")
def boiler_verwarmen_1600_wo_zo():
    """
    Extra comfortrun:
    - woensdag t/m zondag
    - om 16:00
    - 15 minuten boiler aan
    """
    if not _require_bewoond():
        return

    _dbg("Boiler: geforceerde run 16:00 (wo–zo) gestart")
    _switch_on(BOILER_SWITCH)
    task.sleep(FORCED_RUN_MINUTES * 60)
    _switch_off(BOILER_SWITCH)
    _dbg("Boiler: geforceerde run 16:00 (wo–zo) klaar")

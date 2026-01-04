# /config/pyscript/boiler_regeling.py
#
# Slimme boilerregeling:
# - Aan bij teruglevering (export) onder -1100 W
# - Uit bij import boven 1200 W (alleen vóór 16:00)
# - Max 30 min per dag via timer
# - Reset om 06:00
# - Geforceerde run wo–zo om 16:00 (15 min)
#
# NB: task.sleep altijd awaiten in async functies.

from datetime import time

EXPORT_ON_W = -1100 # aan bij levering stroom bij deze grenswaarde
IMPORT_OFF_W = 1200 # uit bij gebruik stroom boven deze grenswaarde
DAILY_TIMER = "00:30:00"

@time_trigger("cron(0 6 * * *)")
async def _reset_0600():
    service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")
    await task.sleep(2)
    service.call("input_boolean", "turn_off", entity_id="input_boolean.boiler_al_verwarmd")
    service.call("timer", "start", entity_id="timer.boiler_opwarmtijd", duration=DAILY_TIMER)
    await task.sleep(1)
    service.call("timer", "pause", entity_id="timer.boiler_opwarmtijd")


def _p1(default: float = 0.0) -> float:
    v = state.get("sensor.p1_meter_power")
    if v in (None, "unknown", "unavailable"):
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


@state_trigger(f"float(sensor.p1_meter_power) < {EXPORT_ON_W}")
def _aan_bij_export():
    if _p1() >= EXPORT_ON_W:
        return
    if state.get("binary_sensor.bewoond") != "on":
        return
    if state.get("input_boolean.boiler_al_verwarmd") != "off":
        return
    if state.get("switch.boiler_stopcontact_1") != "off":
        return
    if state.get("timer.boiler_opwarmtijd") != "paused":
        # Alleen starten als de dag-timer klaarstaat (paused)
        return

    service.call("switch", "turn_on", entity_id="switch.boiler_stopcontact_1")
    service.call("timer", "start", entity_id="timer.boiler_opwarmtijd")


@state_trigger(f"float(sensor.p1_meter_power) > {IMPORT_OFF_W}")
def _uit_bij_import():
    if _p1() <= IMPORT_OFF_W:
        return
    if state.get("switch.boiler_stopcontact_1") != "on":
        return
    if datetime.now().time() >= time(16, 0):
        return

    if state.get("timer.boiler_opwarmtijd") == "active":
        service.call("timer", "pause", entity_id="timer.boiler_opwarmtijd")
    elif state.get("timer.boiler_opwarmtijd") == "idle":
        service.call("input_boolean", "turn_on", entity_id="input_boolean.boiler_al_verwarmd")

    service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")


@event_trigger("timer.finished")
def _timer_finished(event_name=None, data=None, kwargs=None):
    if (data or {}).get("entity_id") != "timer.boiler_opwarmtijd":
        return
    service.call("input_boolean", "turn_on", entity_id="input_boolean.boiler_al_verwarmd")
    service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")


@time_trigger("cron(0 16 * * 3-7)")
async def _forced_1600():
    if state.get("binary_sensor.bewoond") != "on":
        return
    service.call("switch", "turn_on", entity_id="switch.boiler_stopcontact_1")
    await task.sleep(15 * 60)
    service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")

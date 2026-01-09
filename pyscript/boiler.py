# /config/pyscript/boiler_regeling.py
#
# - Aan bij overschot: P1 < -1100 (edge) + bewoond + dagbudget nog niet op + timer staat paused + boiler is uit
# - Uit bij teveel net-afname: P1 > 1200 (edge) vóór 16:00 + boiler is aan
# - Max 30 min/dag via timer (reset 06:00)
# - Geforceerde run wo–zo 16:00 (15 min)
# - Bij HA-start 1x her-evalueren (zonder logspam)

from datetime import datetime, time

AAN_BIJ_OVERSCHOT_W = -1100
UIT_BIJ_NETAFNAME_W = 1200
DAG_TIMER = "00:30:00"

# --------- Edge triggers (geen spam) ---------

@state_trigger(
    f"float(sensor.p1_meter_power) < {AAN_BIJ_OVERSCHOT_W} and "
    f"sensor.p1_meter_power.old is not None and "
    f"float(sensor.p1_meter_power.old) >= {AAN_BIJ_OVERSCHOT_W}"
)
def _aan_edge():
    if state.get("binary_sensor.bewoond") != "on":
        return
    if state.get("input_boolean.boiler_al_verwarmd") != "off":
        return
    if state.get("switch.boiler_stopcontact_1") != "off":
        return
    if state.get("timer.boiler_opwarmtijd") != "paused":
        return

    service.call("switch", "turn_on", entity_id="switch.boiler_stopcontact_1")
    service.call("timer", "start", entity_id="timer.boiler_opwarmtijd")


@state_trigger(
    f"float(sensor.p1_meter_power) > {UIT_BIJ_NETAFNAME_W} and "
    f"sensor.p1_meter_power.old is not None and "
    f"float(sensor.p1_meter_power.old) <= {UIT_BIJ_NETAFNAME_W}"
)
def _uit_edge():
    if state.get("switch.boiler_stopcontact_1") != "on":
        return
    if datetime.now().time() >= time(16, 0):
        return

    if state.get("timer.boiler_opwarmtijd") == "active":
        service.call("timer", "pause", entity_id="timer.boiler_opwarmtijd")
    elif state.get("timer.boiler_opwarmtijd") == "idle":
        service.call("input_boolean", "turn_on", entity_id="input_boolean.boiler_al_verwarmd")

    service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")


# --------- Reset / timers ---------

@time_trigger("cron(0 6 * * *)")
async def _reset_0600():
    service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")
    await task.sleep(2)
    service.call("input_boolean", "turn_off", entity_id="input_boolean.boiler_al_verwarmd")
    service.call("timer", "start", entity_id="timer.boiler_opwarmtijd", duration=DAG_TIMER)
    await task.sleep(1)
    service.call("timer", "pause", entity_id="timer.boiler_opwarmtijd")


@event_trigger("timer.finished")
def _timer_klaar(event_name=None, data=None, kwargs=None):
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


# --------- HA start: 1x evalueren zonder edge ---------

@event_trigger("homeassistant_started")
def _ha_start(event_name=None, data=None, kwargs=None):
    v = state.get("sensor.p1_meter_power")
    try:
        p1 = float(v)
    except (TypeError, ValueError):
        p1 = None

    if p1 is None:
        return

    # eerst veilig uit (als hij aan staat en net-afname te hoog is)
    if p1 > UIT_BIJ_NETAFNAME_W and state.get("switch.boiler_stopcontact_1") == "on" and datetime.now().time() < time(16, 0):
        if state.get("timer.boiler_opwarmtijd") == "active":
            service.call("timer", "pause", entity_id="timer.boiler_opwarmtijd")
        elif state.get("timer.boiler_opwarmtijd") == "idle":
            service.call("input_boolean", "turn_on", entity_id="input_boolean.boiler_al_verwarmd")
        service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")

    # daarna eventueel aan (als er nu genoeg overschot is)
    if p1 < AAN_BIJ_OVERSCHOT_W:
        if state.get("binary_sensor.bewoond") != "on":
            return
        if state.get("input_boolean.boiler_al_verwarmd") != "off":
            return
        if state.get("switch.boiler_stopcontact_1") != "off":
            return
        if state.get("timer.boiler_opwarmtijd") != "paused":
            return
        service.call("switch", "turn_on", entity_id="switch.boiler_stopcontact_1")
        service.call("timer", "start", entity_id="timer.boiler_opwarmtijd")

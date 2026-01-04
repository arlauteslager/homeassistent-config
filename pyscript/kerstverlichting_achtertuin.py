# /config/pyscript/kerstverlichting.py
#
# - Schedule aan/uit -> kerstverlichting aan/uit
# - Achterdeur open (alleen als zon onder & lamp uit):
#   5 min aan, daarna weer uit (reset bij nieuwe deur-open)

_task = None
_token = 0


@state_trigger("schedule.schedule_kerstverlichting_schema == 'on' or schedule.schedule_kerstverlichting_schema == 'off'")
def _schema():
    service.call(
        "light",
        "turn_on" if state.get("schedule.schedule_kerstverlichting_schema") == "on" else "turn_off",
        entity_id="light.kerstverlichting",
    )


@state_trigger("binary_sensor.contact_sensor_deur == 'on'")
def _deur():
    global _task, _token

    if state.get("sun.sun") != "below_horizon":
        return

    # Alleen starten als hij nu uit staat (zoals je oorspronkelijke wens)
    if state.get("light.kerstverlichting") != "off":
        return

    service.call("light", "turn_on", entity_id="light.kerstverlichting")

    # reset / invalideer oude timers
    _token += 1
    my = _token

    if _task is not None:
        try:
            task.cancel(_task)
        except Exception:
            pass
        _task = None

    async def _run():
        await task.sleep(5 * 60)
        if my != _token:
            return
        service.call("light", "turn_off", entity_id="light.kerstverlichting")

    _task = task.create(_run())

OFF_DELAY = 15 * 60
_task = None
_token = 0


def _start_timer():
    global _task, _token
    _token += 1
    my = _token

    if _task is not None:
        try:
            task.cancel(_task)
        except Exception:
            pass
        _task = None

    async def _run(**kwargs):
        await task.sleep(OFF_DELAY)
        if my != _token:
            return
        if state.get("binary_sensor.woonkamer4in1") == "off" and state.get("switch.keukenverlichting") == "on":
            service.call("switch", "turn_off", entity_id="switch.keukenverlichting")

    _task = task.create(_run)   # <-- FIX (geen _run())


@state_trigger("binary_sensor.woonkamer4in1 == 'on'")
def _on():
    global _task, _token
    if state.get("binary_sensor.donker_buiten") != "on":
        return

    service.call("switch", "turn_on", entity_id="switch.keukenverlichting")

    _token += 1
    if _task is not None:
        try:
            task.cancel(_task)
        except Exception:
            pass
        _task = None


@state_trigger("binary_sensor.woonkamer4in1 == 'off'")
def _off():
    if state.get("switch.keukenverlichting") == "on":
        _start_timer()

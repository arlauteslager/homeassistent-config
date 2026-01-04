# /config/pyscript/keukenverlichting.py
#
# - Motion on + donker buiten -> aan
# - Motion off start timer (15 min); geen directe uit
# - Na 15 min: alleen uit als motion nog steeds off
# - Token-guard: oude timers mogen nooit "spook-uit" doen

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

    async def _run():
        await task.sleep(OFF_DELAY)
        if my != _token:
            return
        if state.get("binary_sensor.woonkamer4in1") == "off" and state.get("switch.keukenverlichting") == "on":
            service.call("switch", "turn_off", entity_id="switch.keukenverlichting")

    _task = task.create(_run())


@state_trigger("binary_sensor.woonkamer4in1 == 'on'")
def _on():
    global _task, _token
    if state.get("binary_sensor.donker_buiten") != "on":
        return

    service.call("switch", "turn_on", entity_id="switch.keukenverlichting")

    # maak alle bestaande timers ongeldig + cancel de huidige task
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

# /config/pyscript/voordeur_verlichting.py
#
# - AAN bij activiteit (hal / voordeur / voorkamerdeur) als donker buiten
# - UIT na 15 min zonder activiteit
# - Robuust tegen:
#   * spanningsloze lamp (unavailable)
#   * oude timers (token-guard)

MINUTEN = 15
_task = None
_token = 0


def _light_state_ok():
    return state.get("light.lamp_voordeur") in ("on", "off")


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
        await task.sleep(MINUTEN * 60)
        if my != _token:
            return
        if not _light_state_ok():
            return
        if state.get("light.lamp_voordeur") == "on":
            service.call("light", "turn_off", entity_id="light.lamp_voordeur")

    _task = task.create(_run())


@state_trigger(
    "binary_sensor.sensor_hal == 'on' or "
    "binary_sensor.voordeur == 'on' or "
    "binary_sensor.voorkamerdeur == 'on'"
)
def _activiteit():
    global _task, _token

    if state.get("binary_sensor.donker_buiten") != "on":
        return

    if not _light_state_ok():
        return

    if state.get("light.lamp_voordeur") != "on":
        service.call("light", "turn_on", entity_id="light.lamp_voordeur")

    _token += 1
    if _task is not None:
        try:
            task.cancel(_task)
        except Exception:
            pass
        _task = None

    _start_timer()

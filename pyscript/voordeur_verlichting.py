# /config/pyscript/voordeur_verlichting.py
#
# - AAN bij activiteit (hal / voordeur / voorkamerdeur) als donker buiten
# - UIT na 15 min zonder activiteit (timer reset bij nieuwe activiteit)

MINUTEN = 15
_timer = None


def _reset_timer():
    global _timer

    if _timer is not None:
        try:
            task.cancel(_timer)
        except Exception:
            pass
        _timer = None

    async def _wacht_en_uit():
        await task.sleep(MINUTEN * 60)
        if state.get("light.lamp_voordeur") == "on":
            service.call("light", "turn_off", entity_id="light.lamp_voordeur")

    _timer = task.create(_wacht_en_uit())


@state_trigger(
    "binary_sensor.sensor_hal == 'on' or "
    "binary_sensor.voordeur == 'on' or "
    "binary_sensor.voorkamerdeur == 'on'"
)
def _activiteit():
    if state.get("binary_sensor.donker_buiten") != "on":
        return

    if state.get("light.lamp_voordeur") != "on":
        service.call("light", "turn_on", entity_id="light.lamp_voordeur")

    _reset_timer()

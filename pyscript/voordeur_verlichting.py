# /config/pyscript/voordeur_verlichting.py
#
# - AAN bij activiteit (hal / voordeur / voorkamerdeur) als donker buiten
# - Timer (15 min) wordt bij elke activiteit opnieuw gestart
# - UIT bij timer.finished
# - Robuust tegen unavailable

MINUTEN = 15


def _light_state_ok():
    return state.get("light.lamp_voordeur") in ("on", "off")


@state_trigger(
    "binary_sensor.sensor_hal == 'on' or "
    "binary_sensor.voordeur == 'on' or "
    "binary_sensor.voorkamerdeur == 'on'"
)
def _activiteit():
    if state.get("binary_sensor.donker_buiten") != "on":
        return
    if not _light_state_ok():
        return

    if state.get("light.lamp_voordeur") != "on":
        service.call("light", "turn_on", entity_id="light.lamp_voordeur")

    service.call("timer", "start", entity_id="timer.voordeur_verlichting_off", duration=f"00:{MINUTEN:02d}:00")


@event_trigger("timer.finished")
def _timer_klaar(**kwargs):
    data = kwargs.get("data") or {}
    entity_id = kwargs.get("entity_id") or data.get("entity_id")
    if entity_id != "timer.voordeur_verlichting_off":
        return

    if not _light_state_ok():
        return
    if state.get("light.lamp_voordeur") == "on":
        service.call("light", "turn_off", entity_id="light.lamp_voordeur")

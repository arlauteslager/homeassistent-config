# /config/pyscript/keukenverlichting.py
#
# Gedrag:
# - Beweging + donker buiten -> lamp aan
# - Lamp UIT na 15 minuten GEEN beweging
# - "motion off" triggert NIET direct uit; het start alleen een timer

MOTION = "binary_sensor.woonkamer4in1"
DARK_OUTSIDE = "binary_sensor.donker_buiten"
KITCHEN_LIGHT = "switch.keukenverlichting"

OFF_DELAY_SECONDS = 15 * 60  # 15 minuten

_off_task = None


def _light_on():
    if state.get(KITCHEN_LIGHT) != "on":
        service.call("switch", "turn_on", entity_id=KITCHEN_LIGHT)


def _light_off():
    if state.get(KITCHEN_LIGHT) != "off":
        service.call("switch", "turn_off", entity_id=KITCHEN_LIGHT)


def _cancel_off_task():
    global _off_task
    if _off_task is not None:
        try:
            _off_task.cancel()
        except Exception:
            pass
        _off_task = None


def _start_off_timer():
    """
    Start/restart de uit-timer:
    - wacht 15 min
    - zet uit als er nog steeds geen beweging is
    """
    global _off_task
    _cancel_off_task()

    def _runner():
        task.sleep(OFF_DELAY_SECONDS)
        if state.get(MOTION) == "off":
            _light_off()

    _off_task = task.create(_runner)


@state_trigger(f"{MOTION} == 'on'")
def keukenverlichting_motion_on():
    # Alleen aansturen als het donker buiten is
    if state.get(DARK_OUTSIDE) != "on":
        return

    _light_on()

    # Elke beweging annuleert de uit-timer (reset)
    _cancel_off_task()


@state_trigger(f"{MOTION} == 'off'")
def keukenverlichting_motion_off():
    # Geen directe actie bij 'off' behalve timer starten
    if state.get(KITCHEN_LIGHT) != "on":
        return

    _start_off_timer()

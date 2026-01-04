# /config/pyscript/hal_verlichting.py

from datetime import datetime, time

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
        if state.get("light.verlichting_hal") == "on":
            service.call("light", "turn_off", entity_id="light.verlichting_hal")

    _timer = task.create(_wacht_en_uit())


def _hal_aan_en_timer():
    if state.get("binary_sensor.donker_buiten") != "on":
        return

    if state.get("light.verlichting_hal") != "on":
        service.call("light", "turn_on", entity_id="light.verlichting_hal")

    _reset_timer()


@state_trigger(
    "binary_sensor.sensor_hal == 'on' or "
    "binary_sensor.voordeur == 'on' or "
    "binary_sensor.voorkamerdeur == 'on'"
)
def _hal_deuren():
    _hal_aan_en_timer()


@state_trigger("binary_sensor.overloop4in1 == 'on'")
def _overloop():
    t = datetime.now().time()
    if not (time(7, 0) <= t <= time(23, 59, 59)):
        return

    _hal_aan_en_timer()

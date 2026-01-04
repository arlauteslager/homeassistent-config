# /config/pyscript/hal_verlichting.py

from datetime import datetime, time

MINUTEN = 15
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
        await task.sleep(MINUTEN * 60)
        if my != _token:
            return
        if state.get("light.verlichting_hal") == "on":
            service.call("light", "turn_off", entity_id="light.verlichting_hal")

    _task = task.create(_run())


def _activity():
    global _task, _token

    if state.get("binary_sensor.donker_buiten") != "on":
        return

    if state.get("light.verlichting_hal") != "on":
        service.call("light", "turn_on", entity_id="light.verlichting_hal")

    # invalideer alle oudere timers (ook als cancel faalt)
    _token += 1

    if _task is not None:
        try:
            task.cancel(_task)
        except Exception:
            pass
        _task = None


@state_trigger(
    "binary_sensor.sensor_hal == 'on' or "
    "binary_sensor.voordeur == 'on' or "
    "binary_sensor.voorkamerdeur == 'on'"
)
def _hal_deuren():
    _activity()


@state_trigger("binary_sensor.overloop4in1 == 'on'")
def _overloop():
    t = datetime.now().time()
    if not (time(7, 0) <= t <= time(23, 59, 59)):
        return
    _activity()


@state_trigger(
    "binary_sensor.sensor_hal == 'off' or "
    "binary_sensor.voordeur == 'off' or "
    "binary_sensor.voorkamerdeur == 'off' or "
    "binary_sensor.overloop4in1 == 'off'"
)
def _off_events_start_timer():
    # Alleen timer starten als het licht aan staat; uit gebeurt na MINUTEN zonder nieuwe 'on'
    if state.get("light.verlichting_hal") == "on":
        _start_timer()

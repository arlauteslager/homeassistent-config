# /config/pyscript/tv.py
#
# - Dagelijks 00:25: TV-stopcontact uit (behalve 1 januari)
# - Beweging woonkamer: TV-stopcontact aan binnen tijdvensters, alleen als nu uit

from datetime import datetime, time

_windows = {
    "sat": [("07:00", "12:00")],
    "sun": [("07:00", "11:00")],
    "thu": [("12:00", "18:00")],
    "fri": [("13:00", "17:00")],
}
_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _allowed(now: datetime) -> bool:
    d = _days[now.weekday()]
    t = now.time()
    for a, b in _windows.get(d, []):
        if time.fromisoformat(a) <= t < time.fromisoformat(b):
            return True
    return False


@time_trigger("cron(25 0 * * *)")
def _off_0025():
    now = datetime.now()
    if now.strftime("%m-%d") == "01-01":
        return
    service.call("switch", "turn_off", entity_id="switch.tv_stopcontact_1")


@state_trigger("binary_sensor.woonkamer4in1 == 'on'")
def _on_motion():
    now = datetime.now()
    if not _allowed(now):
        return
    if state.get("switch.tv_stopcontact_1") != "off":
        return
    service.call("switch", "turn_on", entity_id="switch.tv_stopcontact_1")

# pyscript/planten_water.py

from datetime import datetime

PLANTS = [
    {"name": "Watermunt", "entity": "sensor.watermunt_luchtvochtigheid", "thr": 30},
    {"name": "Pannenkoekenplant", "entity": "sensor.pannekoekenplant_luchtvochtigheid", "thr": 10},
    # Voeg later planten toe:
    # {"name": "Basilicum", "entity": "sensor.basilicum_grondvocht", "thr": 25},
]

NOTIFY = "notify.mobile_app_iphone_13_arnaud"  # <-- aanpassen
AT = "20:00:00"  # dagelijkse reminder tijd

def _as_float(s):
    try:
        return float(s)
    except Exception:
        return None

def _msg(p, v):
    return f"{p['name']} is te droog ({v:.1f}% < {p['thr']}%). Tijd om water te geven."

def _notify(title, message):
    # notify.* services hebben doorgaans title/message
    service.call(NOTIFY, title=title, message=message)

@time_trigger(f"cron({AT.split(':')[1]} {AT.split(':')[0]} * * *)")
def planten_daily_reminder():
    msgs = []
    for p in PLANTS:
        v = _as_float(state.get(p["entity"]))
        if v is not None and v < p["thr"]:
            msgs.append(_msg(p, v))
    if msgs:
        _notify("🌿 Plant water geven", "\n".join(msgs))

# Directe melding als een plant onder de drempel komt
@state_trigger("sensor.watermunt_luchtvochtigheid")
def watermunt_direct():
    v = _as_float(state.get("sensor.watermunt_luchtvochtigheid"))
    if v is not None and v < 30:
        _notify("🌿 Plant water geven", _msg({"name":"Watermunt","thr":30}, v))

@state_trigger("sensor.pannekoekenplant_luchtvochtigheid")
def pannekoek_direct():
    v = _as_float(state.get("sensor.pannekoekenplant_luchtvochtigheid"))
    if v is not None and v < 10:
        _notify("🌿 Plant water geven", _msg({"name":"Pannenkoekenplant","thr":10}, v))

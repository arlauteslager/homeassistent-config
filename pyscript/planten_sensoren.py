# pyscript/planten_sensoren.py

MOBILE = "mobile_app_iphone_13_arnaud"


def _to_float(x):
    if x in (None, "unknown", "unavailable"):
        return None
    try:
        return float(str(x).replace("%", "").strip())
    except Exception:
        return None


@time_trigger(f"cron( 0 19 * * *)")
def planten_daily_reminder():
    msgs = []

    v = _to_float(state.get("sensor.watermunt_luchtvochtigheid"))
    if v is not None and v < 40:
        msgs.append(f"Watermunt is te droog ({v:.1f}% < 40%). Tijd om water te geven.")

    v = _to_float(state.get("sensor.pannekoekenplant_luchtvochtigheid"))
    if v is not None and v < 25:
        msgs.append(f"Pannenkoekenplant is te droog ({v:.1f}% < 25%). Tijd om water te geven.")

    v = _to_float(state.get("sensor.adoptieplant_luchtvochtigheid"))
    if v is not None and v < 30:
        msgs.append(f"adoptieplant is te droog ({v:.1f}% < 30%). Tijd om water te geven.")

    v = _to_float(state.get("sensor.duin_watermunt_luchtvochtigheid"))
    if v is not None and v < 40:
        msgs.append(f"duin-watermuntplant is te droog ({v:.1f}% < 40%). Tijd om water te geven.")
    if msgs:
        service.call("notify", MOBILE, title="🌿 Plant water geven", message="\n".join(msgs))


# @state_trigger("sensor.watermunt_luchtvochtigheid")
# def watermunt_direct():
#     v = _to_float(state.get("sensor.watermunt_luchtvochtigheid"))
#     if v is not None and v < 30:
#         service.call("notify", MOBILE, title="🌿 Plant water geven",
#             message=f"Watermunt is te droog ({v:.1f}% < 30%). Tijd om water te geven.")


# @state_trigger("sensor.pannekoekenplant_luchtvochtigheid")
# def pannenkoekenplant_direct():
#     v = _to_float(state.get("sensor.pannekoekenplant_luchtvochtigheid"))
#     if v is not None and v < 10:
#         service.call("notify", MOBILE, title="🌿 Plant water geven",
#             message=f"Pannenkoekenplant is te droog ({v:.1f}% < 10%). Tijd om water te geven.")

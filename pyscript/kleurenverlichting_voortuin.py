# /config/pyscript/kleurentuinverlichting.py
#
# Kleurentuinverlichting:
# - Volgt exact het schedule (aan bij on, uit bij off)

@state_trigger(
    "schedule.kleurentuinverlichting_schema == 'on' or "
    "schedule.kleurentuinverlichting_schema == 'off'"
)
def _schema():
    service.call(
        "switch",
        "turn_on" if state.get("schedule.kleurentuinverlichting_schema") == "on" else "turn_off",
        entity_id="switch.kleurentuinverlichting",
    )

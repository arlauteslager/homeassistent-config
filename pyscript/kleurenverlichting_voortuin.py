# /config/pyscript/kleurentuinverlichting.py
#
# Omzetting van:
# kleurentuinverlichting op schedule (alleen begin/einde tijdvak)

SCHEDULE = "schedule.kleurentuinverlichting_schema"
SWITCH = "switch.kleurentuinverlichting"


@state_trigger(f"{SCHEDULE} == 'on' or {SCHEDULE} == 'off'")
def kleurentuinverlichting_op_schedule():
    if state.get(SCHEDULE) == "on":
        service.call("switch", "turn_on", entity_id=SWITCH)
    else:
        service.call("switch", "turn_off", entity_id=SWITCH)

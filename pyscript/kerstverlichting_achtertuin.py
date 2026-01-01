# /config/pyscript/kerstverlichting.py
#
# Functionaliteit:
# 1) Schema (schedule) zet kerstverlichting aan of uit bij begin/einde tijdvak
# 2) Achterdeur open:
#    - alleen als zon onder is
#    - alleen als lamp nu uit staat
#    - lamp 5 minuten aan, daarna weer uit

SCHEDULE = "schedule.schedule_kerstverlichting_schema"
LIGHT = "light.kerstverlichting"
DOOR = "binary_sensor.contact_sensor_deur"
SUN = "sun.sun"


@state_trigger(f"{SCHEDULE} == 'on' or {SCHEDULE} == 'off'")
def kerstverlichting_op_schema():
    if state.get(SCHEDULE) == "on":
        service.call("light", "turn_on", entity_id=LIGHT)
    else:
        service.call("light", "turn_off", entity_id=LIGHT)


@state_trigger(f"{DOOR} == 'on'")
def kerstverlichting_op_achterdeur():
    # Alleen inschakelen als zon onder is en lamp uit staat
    if state.get(SUN) != "below_horizon":
        return
    if state.get(LIGHT) != "off":
        return

    service.call("light", "turn_on", entity_id=LIGHT)

    # 5 minuten wachten
    task.sleep(5 * 60)

    service.call("light", "turn_off", entity_id=LIGHT)

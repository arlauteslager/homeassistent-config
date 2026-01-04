# /config/pyscript/kerstverlichting.py
#
# - Schedule aan/uit -> kerstverlichting aan/uit
# - Achterdeur open (alleen als zon onder & lamp uit):
#   5 min aan, daarna weer uit

@state_trigger("schedule.schedule_kerstverlichting_schema == 'on' or schedule.schedule_kerstverlichting_schema == 'off'")
def _schema():
    service.call(
        "light",
        "turn_on" if state.get("schedule.schedule_kerstverlichting_schema") == "on" else "turn_off",
        entity_id="light.kerstverlichting",
    )


@state_trigger("binary_sensor.contact_sensor_deur == 'on'")
async def _deur():
    if state.get("sun.sun") != "below_horizon":
        return
    if state.get("light.kerstverlichting") != "off":
        return

    service.call("light", "turn_on", entity_id="light.kerstverlichting")
    await task.sleep(5 * 60)
    service.call("light", "turn_off", entity_id="light.kerstverlichting")

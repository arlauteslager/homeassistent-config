# /config/pyscript/keukenverlichting.py
#
# - Motion on + donker buiten -> aan
# - Motion off start timer (15 min); geen directe uit
# - Na 15 min: alleen uit als motion nog steeds off

OFF_DELAY = 15 * 60
_off = None


def _cancel():
    global _off
    if _off is not None:
        try:
            task.cancel(_off)
        except Exception:
            pass
        _off = None


def _start_timer():
    global _off
    _cancel()

    async def _runner():
        await task.sleep(OFF_DELAY)
        if state.get("binary_sensor.woonkamer4in1") == "off" and state.get("switch.keukenverlichting") == "on":
            service.call("switch", "turn_off", entity_id="switch.keukenverlichting")

    _off = task.create(_runner())


@state_trigger("binary_sensor.woonkamer4in1 == 'on'")
def _motion_on():
    if state.get("binary_sensor.donker_buiten") != "on":
        return
    service.call("switch", "turn_on", entity_id="switch.keukenverlichting")
    _cancel()


@state_trigger("binary_sensor.woonkamer4in1 == 'off'")
def _motion_off():
    if state.get("switch.keukenverlichting") != "on":
        return
    _start_timer()

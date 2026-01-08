# /config/pyscript/bewoond_bepalen.py
#
# Dag-latch: iphone_vandaag_gezien
# - Reset om 06:50
# - Vanaf 11:00 latch aan als iPhone thuis is (niet tijdens vakantie)
# - Vakantie aan: latch altijd uit

from datetime import datetime, time as dtime

def _eval():
    if state.get("input_boolean.vakantie") == "on":
        return

    if datetime.now().time() < dtime(11, 0):
        return

    if state.get("device_tracker.iphone13arnaud") == "home" and state.get("input_boolean.iphone_vandaag_gezien") != "on":
        service.call("input_boolean", "turn_on", entity_id="input_boolean.iphone_vandaag_gezien")


@state_trigger("device_tracker.iphone13arnaud")
def _iphone_change():
    if state.get("device_tracker.iphone13arnaud") == "home":
        _eval()


@time_trigger("cron(0 11 * * *)")
def _om_11u():
    _eval()


@time_trigger("cron(50 6 * * *)")
def _reset_6u():
    service.call("input_boolean", "turn_off", entity_id="input_boolean.iphone_vandaag_gezien")


@state_trigger("input_boolean.vakantie == 'on'")
def _vakantie_on():
    service.call("input_boolean", "turn_off", entity_id="input_boolean.iphone_vandaag_gezien")


@state_trigger("input_boolean.vakantie == 'off'")
def _vakantie_off():
    _eval()

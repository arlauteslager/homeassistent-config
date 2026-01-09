# /config/pyscript/kachel_werkkamer_auto_uit.py

@state_trigger("binary_sensor.arnaud_thuis == 'off'")
def kachel_werkkamer_uit_als_arnaud_vertrekt():
    if state.get("switch.kachel_werkkamer_socket_1") != "on":
        return

    service.call("switch", "turn_off", entity_id="switch.kachel_werkkamer_socket_1")

    service.call(
        "notify",
        "mobile_app_iphone_13_arnaud",
        title="Kachel werkkamer",
        message="Arnaud is niet thuis: kachel werkkamer uitgezet.",
    )

    log.warning("[kachel_werkkamer] Arnaud niet thuis -> kachel uitgezet + pushmelding")


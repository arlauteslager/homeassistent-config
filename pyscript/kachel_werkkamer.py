# /config/pyscript/kachel_werkkamer_auto_uit.py
#
# Doel:
# - Als Arnaud thuis -> off (niet thuis),
#   en de kachel in de werkkamer staat nog aan,
#   zet die dan uit + maak een persistent notification.

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

    log.info("[kachel_werkkamer] Arnaud niet thuis -> kachel uitgezet + notification")

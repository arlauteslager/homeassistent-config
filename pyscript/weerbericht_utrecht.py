# /config/pyscript/knmi_weerbericht_utrecht.py
#
# Omzetting van jouw automation:
# - Do/vr om 07:25: weerbericht Utrecht voorlezen
# - Za/zo om 10:00: weerbericht Utrecht voorlezen
# - Eerst REST sensor verversen
# - Wachten tot full_text gevuld is (max 10s)
# - Fallback tekst als niet beschikbaar
# - Voorlezen via script.tts_with_smart_volume naar media_player.achterkamer

from datetime import datetime

UPDATE_ENTITY = "sensor.knmi_data_utrecht"
WEER_SENSOR = "sensor.knmi_weerbericht_utrecht"
PLAYER = "media_player.achterkamer"


def _is_valid_text(t) -> bool:
    return t not in (None, "", "unknown", "unavailable")


@time_trigger("cron(25 7 * * 3,4)")   # donderdag(3) en vrijdag(4) om 07:25
@time_trigger("cron(0 10 * * 5,6)")  # zaterdag(5) en zondag(6) om 10:00
def lees_knmi_weerbericht_utrecht_op_dagen():
    # 1) Sensor verversen
    service.call("homeassistant", "update_entity", entity_id=UPDATE_ENTITY)

    # 2) Wachten tot full_text gevuld is (max 10 seconden)
    weer_text = None
    deadline = datetime.now().timestamp() + 10

    while datetime.now().timestamp() < deadline:
        t = state.get(f"{WEER_SENSOR}.full_text")
        if _is_valid_text(t):
            weer_text = t
            break
        task.sleep(0.5)

    # 3) Fallback
    if not _is_valid_text(weer_text):
        weer_text = "Het weerbericht voor Utrecht is nu niet beschikbaar."

    # 4) Voorlezen via jouw TTS-script
    service.call(
        "script",
        "tts_with_smart_volume",
        player=PLAYER,
        text=f"Goedemorgen, het weerbericht voor Utrecht: {weer_text}",
        volume=0.35,
    )

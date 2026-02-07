# /config/pyscript/knmi_weerbericht_utrecht.py
#
# - Do/vr 07:25 en za/zo 10:00: KNMI weerbericht Utrecht voorlezen
# - Eerst update_entity
# - Wacht max 10s op .full_text (poll elke 0.5s)
# - Fallback tekst
# - TTS via script.tts_with_smart_volume

from datetime import datetime

@time_trigger("cron(25 7 * * 3,4)")
@time_trigger("cron(0 10 * * 5,6)")
async def _knmi():
    service.call("homeassistant", "update_entity", entity_id="sensor.knmi_data_utrecht")

    text = None
    deadline = datetime.now().timestamp() + 10

    while datetime.now().timestamp() < deadline:
        t = state.get("sensor.knmi_weerbericht_utrecht.full_text")
        if t not in (None, "", "unknown", "unavailable"):
            text = t
            break
        await task.sleep(5)

    if text in (None, "", "unknown", "unavailable"):
        text = "Het weerbericht voor Utrecht is nu niet beschikbaar."

    service.call(
        "script",
        "tts_with_smart_volume",
        player="media_player.achterkamer",
        text=f"Goedemorgen, het weerbericht voor Utrecht: {text}",
        volume=0.35,
    )

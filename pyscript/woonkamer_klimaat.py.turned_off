# /config/pyscript/woonkamer_klimaat.py
#
# - Bij beweging: melding via TTS, max 1x/uur (timer cooldown)
# - Alleen als te vochtig of te droog

@state_trigger("binary_sensor.woonkamer4in1 == 'on'")
def _klimaat_melding():
    if state.get("timer.woonkamer_klimaat_melding_cooldown") != "idle":
        return

    humid = (state.get("binary_sensor.woonkamer_klimaat_te_vochtig") == "on")
    dry = (state.get("binary_sensor.woonkamer_klimaat_te_droog") == "on")
    if not (humid or dry):
        return

    try:
        t = float(state.get("sensor.woonkamerklimaat_temperatuur"))
    except (TypeError, ValueError):
        t = 0.0

    try:
        rh = float(state.get("sensor.woonkamerklimaat_luchtvochtigheid"))
    except (TypeError, ValueError):
        rh = 0.0

    msg = (
        "Let op. De lucht is te vochtig in de woonkamer. "
        f"Temperatuur {t:.1f} graden, luchtvochtigheid {rh:.0f} procent. "
        "Advies: ventileer of verwarm kort om schimmel te voorkomen."
        if humid else
        "Let op. De lucht is te droog in de woonkamer. "
        f"Temperatuur {t:.1f} graden, luchtvochtigheid {rh:.0f} procent. "
        "Advies: eventueel tijdelijk bevochtigen."
    )

    service.call(
        "script",
        "tts_with_smart_volume",
        player="media_player.achterkamer",
        text=msg,
        volume=0.35,
    )
    service.call("timer", "start", entity_id="timer.woonkamer_klimaat_melding_cooldown")

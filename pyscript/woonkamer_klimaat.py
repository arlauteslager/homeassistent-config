# /config/pyscript/woonkamer_klimaat.py
#
# Omzetting van:
# "Woonkamer klimaat: melding bij beweging (Sonos, max 1x/uur)"
#
# Trigger: beweging (binary_sensor.woonkamer4in1 -> on)
# Conditions:
# - timer cooldown moet idle zijn
# - óf te_vochtig óf te_droog moet on zijn
# Action:
# - lees T en RH
# - spreek via script.tts_with_smart_volume
# - start cooldown timer

W_MOTION = "binary_sensor.woonkamer4in1"
TIMER_COOLDOWN = "timer.woonkamer_klimaat_melding_cooldown"
TOO_HUMID = "binary_sensor.woonkamer_klimaat_te_vochtig"
TOO_DRY = "binary_sensor.woonkamer_klimaat_te_droog"

S_T = "sensor.woonkamerklimaat_temperatuur"
S_RH = "sensor.woonkamerklimaat_luchtvochtigheid"


def _float_state(entity_id: str, default: float = 0.0) -> float:
    """Lees state als float, met fallback."""
    try:
        return float(state.get(entity_id))
    except (TypeError, ValueError):
        return default


@state_trigger(f"{W_MOTION} == 'on'")
def woonkamer_klimaat_melding_bij_beweging():
    # Cooldown: max 1x per uur (timer moet idle zijn)
    if state.get(TIMER_COOLDOWN) != "idle":
        return

    # Alleen melden als te vochtig of te droog
    humid = state.get(TOO_HUMID) == "on"
    dry = state.get(TOO_DRY) == "on"
    if not (humid or dry):
        return

    # Sensorwaarden ophalen
    T = _float_state(S_T, 0.0)
    RH = _float_state(S_RH, 0.0)

    # Bericht bepalen
    if humid:
        message = (
            "Let op. De lucht is te vochtig in de woonkamer. "
            f"Temperatuur {T:.1f} graden, luchtvochtigheid {RH:.0f} procent. "
            "Advies: ventileer of verwarm kort om schimmel te voorkomen."
        )
    else:  # dry
        message = (
            "Let op. De lucht is te droog in de woonkamer. "
            f"Temperatuur {T:.1f} graden, luchtvochtigheid {RH:.0f} procent. "
            "Advies: eventueel tijdelijk bevochtigen."
        )

    # Spreek via jouw Sonos TTS script
    service.call("script", "tts_with_smart_volume", message=message)

    # Start cooldown timer (duur regel je in de timer-config zelf)
    service.call("timer", "start", entity_id=TIMER_COOLDOWN)

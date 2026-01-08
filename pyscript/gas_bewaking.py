# /config/pyscript/gas_bewaking.py
#
# Elk uur:
# - lees gasmeterstand (m³) uit sensor.gas_meter_gas
# - bepaal of stand gestegen is t.o.v. vorige uur
# - tel opeenvolgende uren met stijging
# - bij 3 uren op rij stijging:
#     * 1x persistent notification
#     * elk uur een Sonos-bericht (achterkamer) zolang de reeks doorloopt

from datetime import datetime

SENSOR = "sensor.gas_meter_gas"
EPS = 0.0001  # tolerantie voor afronding/float-ruis

PLAYER = "media_player.achterkamer"
TTS_SCRIPT = "script.tts_with_smart_volume"
TTS_TEXT = "Ha bewoner, staat de CV nog aan? Ik zie namelijk dat er 3 achteenvolgende uren gas wordt gebruikt"

_last_value = None
_streak = 0
_notified = False


def _as_float(entity_id: str):
    v = state.get(entity_id)
    if v in (None, "unknown", "unavailable"):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _speak():
    # Speel bericht af via jouw bestaande Sonos TTS script
    service.call(
        "script",
        "tts_with_smart_volume",
        player=PLAYER,
        text=TTS_TEXT,
        volume=0.35,  # pas aan als je wilt
    )


@time_trigger("cron(0 * * * *)")  # elk uur op minuut 0
def gas_check_hourly():
    global _last_value, _streak, _notified

    now = datetime.now()
    cur = _as_float(SENSOR)
    if cur is None:
        log.warning("[gas_bewaking] %s: sensor heeft geen geldige waarde (%s)", now, state.get(SENSOR))
        return

    # Eerste run: alleen initialiseren
    if _last_value is None:
        _last_value = cur
        _streak = 0
        _notified = False
        log.info("[gas_bewaking] %s: init last_value=%.5f", now, cur)
        return

    delta = cur - _last_value
    increased = delta > EPS

    if increased:
        _streak += 1
        log.info("[gas_bewaking] %s: gas gestegen (Δ=%.5f m³), streak=%d", now, delta, _streak)
    else:
        # reeks breekt -> reset en notificatie opnieuw toestaan
        if _streak != 0 or _notified:
            log.info("[gas_bewaking] %s: geen stijging (Δ=%.5f m³), reset streak", now, delta)
        _streak = 0
        _notified = False

    # Bewaar huidige stand voor volgende uur
    _last_value = cur

    # Bij 4+ achtereenvolgende uren stijging:
    # - 1x persistent notification (per streak)
    # - ELK uur Sonos bericht zolang streak >= 3
    if _streak >= 3:
        if not _notified:
            service.call(
                "notify",
                "mobile_app_iphone_13_arnaud",
                title="Gasbewaking",
                message="Staat de CV nog aan? Ik zie namelijk dat er 3 achteenvolgende uren gas wordt gebruikt",
            )
            _notified = True

        # elk uur herhalen zolang de reeks doorloopt
        _speak()

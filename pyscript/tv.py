# /config/pyscript/tv.py
#
# Doel (menselijk):
# 1) Elke dag om 00:25: TV-stopcontact UIT, behalve op 1 januari.
#    + schrijf een logboekregel.
# 2) Bij beweging in de woonkamer: TV-stopcontact AAN,
#    maar alleen binnen ingestelde tijdvensters en alleen als hij nu uit staat.

from datetime import datetime, time

TV_SWITCH = "switch.tv_stopcontact_1"
MOTION_SENSOR = "binary_sensor.woonkamer4in1"

# Tijdvensters waarin beweging de TV mag inschakelen
#
# Structuur:
#   "<dag>": [("HH:MM", "HH:MM"), ...]
#
# Dagen:
#   mon, tue, wed, thu, fri, sat, sun
WINDOWS = {
    "sat": [("07:00", "12:00")],  # zaterdag ochtend
    "sun": [("07:00", "11:00")],  # zondag ochtend
    "thu": [("12:00", "18:00")],  # donderdag middag
    "fri": [("13:00", "17:00")],  # vrijdag middag
}

DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def in_allowed_window(now: datetime) -> bool:
    """True als 'now' binnen één van de ingestelde tijdvensters valt."""
    day = DAY_NAMES[now.weekday()]
    current = now.time()

    for start_str, end_str in WINDOWS.get(day, []):
        start = time.fromisoformat(start_str)
        end = time.fromisoformat(end_str)
        if start <= current < end:
            return True

    return False


@time_trigger("cron(25 0 * * *)")  # dagelijks om 00:25
def tv_off_daily():
    now = datetime.now()

    # 1 januari overslaan
    if now.strftime("%m-%d") == "01-01":
        log.info("TV schema: 1 januari -> overslaan")
        return

    # TV-stopcontact uit
    service.call("switch", "turn_off", entity_id=TV_SWITCH)

    # Logboekregel (zoals je YAML automation)
    service.call(
        "logbook",
        "log",
        message=f"tv stopcontact uitgeschakeld om {now:%Y-%m-%d %H:%M:%S}",
    )


@state_trigger(f"{MOTION_SENSOR} == 'on'")
def tv_on_motion():
    now = datetime.now()

    # Alleen binnen toegestane vensters
    if not in_allowed_window(now):
        return

    # Alleen aanzetten als hij echt uit is
    if state.get(TV_SWITCH) != "off":
        return

    # TV-stopcontact aan
    service.call("switch", "turn_on", entity_id=TV_SWITCH)


# Optioneel (handig): handmatige tests via Developer Tools → Services
@service
def tv_test_off():
    """Simuleer de 00:25-actie (handig voor testen)."""
    tv_off_daily()


@service
def tv_test_on_if_allowed():
    """Simuleer de motion-actie (zet alleen aan als je binnen een venster zit)."""
    tv_on_motion()

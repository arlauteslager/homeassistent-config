# -------------------------------------------------------------------
# Hal & voordeur verlichting – activiteit gestuurd met failsafe
#
# Gedrag:
# - Lampen gaan AAN bij activiteit (beweging / deur open)
# - Alleen als het buiten donker is
# - Lampen gaan UIT na 15 minuten ZONDER activiteit
# - Elke nieuwe activiteit start de 15 minuten opnieuw
# - Overloop telt alleen mee voor de hal en alleen tussen 07:00–00:00
# -------------------------------------------------------------------

from datetime import datetime, time

# =========================
# Configuratie
# =========================

# Sensoren
SENSOR_HAL = "binary_sensor.sensor_hal"
SENSOR_VOORDEUR = "binary_sensor.voordeur"
SENSOR_VOORKAMER = "binary_sensor.voorkamerdeur"
SENSOR_OVERLOOP = "binary_sensor.overloop4in1"
SENSOR_DONKER = "binary_sensor.donker_buiten"

# Lampen
LICHT_HAL = "light.verlichting_hal"
LICHT_VOORDEUR = "light.lamp_voordeur"

# Instellingen
MINUTEN_ZONDER_ACTIVITEIT = 15


# =========================
# Interne status (timers)
# =========================

_hal_timer = None
_voordeur_timer = None


# =========================
# Hulpfuncties
# =========================

def is_donker() -> bool:
    """True als het buiten donker is."""
    return state.get(SENSOR_DONKER) == "on"


def overloop_mag_meedoen() -> bool:
    """Overloop telt alleen overdag / avond."""
    return datetime.now().time() >= time(7, 0)


def zet_licht_aan(entity_id: str):
    """Zet een lamp aan (veilig, ook als hij al aan staat)."""
    service.call("light", "turn_on", entity_id=entity_id)


def zet_licht_uit(entity_id: str):
    """Zet een lamp uit."""
    service.call("light", "turn_off", entity_id=entity_id)


def start_of_reset_timer(welke: str, licht: str):
    """
    Start of reset de 'uit-na-geen-activiteit' timer.
    Elke nieuwe activiteit zet de teller opnieuw op 15 minuten.
    """
    global _hal_timer, _voordeur_timer

    # Bepaal welke timer we gebruiken
    huidige_timer = _hal_timer if welke == "hal" else _voordeur_timer

    # Stop oude timer (reset)
    if huidige_timer is not None:
        try:
            task.cancel(huidige_timer)
        except Exception:
            pass

    # Start nieuwe timer
    def wacht_en_zet_uit():
        task.sleep(MINUTEN_ZONDER_ACTIVITEIT * 60)
        if state.get(licht) == "on":
            zet_licht_uit(licht)

    nieuwe_timer = task.create(wacht_en_zet_uit())

    if welke == "hal":
        _hal_timer = nieuwe_timer
    else:
        _voordeur_timer = nieuwe_timer


# =========================
# Activiteit handlers
# =========================

def activiteit_bij_hal_of_deur():
    """
    Activiteit bij hal of (voor)deur:
    - Hal- én voordeurlicht aan
    - Timers resetten
    """
    if not is_donker():
        return

    zet_licht_aan(LICHT_HAL)
    zet_licht_aan(LICHT_VOORDEUR)

    start_of_reset_timer("hal", LICHT_HAL)
    start_of_reset_timer("voordeur", LICHT_VOORDEUR)


def activiteit_op_overloop():
    """
    Activiteit op de overloop:
    - Alleen hallicht
    - Alleen als donker én niet 's nachts
    """
    if not is_donker():
        return
    if not overloop_mag_meedoen():
        return

    zet_licht_aan(LICHT_HAL)
    start_of_reset_timer("hal", LICHT_HAL)


# =========================
# Triggers
# =========================

@state_trigger(
    f"{SENSOR_HAL} == 'on' or "
    f"{SENSOR_VOORDEUR} == 'on' or "
    f"{SENSOR_VOORKAMER} == 'on'"
)
def trigger_hal_en_deuren():
    activiteit_bij_hal_of_deur()


@state_trigger(f"{SENSOR_OVERLOOP} == 'on'")
def trigger_overloop():
    activiteit_op_overloop()


# =========================
# Handige test-services
# =========================

@service
def test_hal_activiteit():
    """Handmatig testen: alsof er beweging bij hal/deur is."""
    activiteit_bij_hal_of_deur()


@service
def test_overloop_activiteit():
    """Handmatig testen: alsof er beweging op de overloop is."""
    activiteit_op_overloop()

# /config/pyscript/boiler.py
#
# Functionaliteit van dit script
# ------------------------------
# Dit script stuurt de boiler op basis van zonne-overschot, batterijstatus
# en een dagtimer.
#
# Gedrag:
# - De boiler mag vóór 15:00 starten als:
#   - de boiler die dag nog niet volledig is verwarmd;
#   - de timer nog resterende opwarmtijd heeft;
#   - de batterij minimaal 70% vol is;
#   - de P1-meter voldoende teruglevering laat zien.
# - De startvoorwaarde moet eerst 30 seconden aaneengesloten waar zijn.
# - Daarna wordt de start nog 3 keer extra gevalideerd met 5 seconden ertussen.
# - Tijdens dit zonneladen stopt de boiler pas als er 30 seconden
#   aaneengesloten meer dan de ingestelde netafname wordt gemeten.
# - De boiler mag maximaal 30 minuten per dag verwarmen via de timer.
# - Als de boiler om 15:00 nog niet klaar is, start hij alsnog via het net
#   met de resterende timertijd.
# - Alleen deze geforceerde laadrun om 15:00 gebruikt de controle op 'bewoond'.
# - Elke dag om 06:00 worden schakelaar, boolean en timer opnieuw klaargezet.
# - Logging gaat alleen naar de pyscript-log.

from datetime import datetime, time

DAG_TIMER = "00:30:00"
START_TERUGLEVERING_W = -1200
STOP_NETAFNAME_W = 400
DEBUG = 1


# Logt een technische regel naar de pyscript-log.
def log_boiler(actie, reden=""):
    msg = actie if reden == "" else f"{actie} - {reden}"
    log.info(f"Boiler: {msg}")


# Controleert of de boiler op dit moment op zonne-overschot mag starten.
def mag_op_zon_starten():
    try:
        p1 = float(state.get("sensor.p1_meter_power"))
        soc = float(state.get("sensor.nextenergy_bms_soc"))
    except (TypeError, ValueError):
        return False

    if datetime.now().time() >= time(15, 0):
        return False
    if p1 > START_TERUGLEVERING_W:
        return False
    if soc < 70:
        return False
    if state.get("input_boolean.boiler_al_verwarmd") != "off":
        return False
    if state.get("switch.boiler_stopcontact_1") != "off":
        return False
    if state.get("timer.boiler_opwarmtijd") != "paused":
        return False

    return True


# Controleert na de eerste 30 seconden nog 3 keer met 5 seconden tussenpauze
# of de startvoorwaarde nog steeds geldig is.
async def start_validatie():
    if DEBUG == 1:
        log.info("Boiler debug | start_validatie gestart")

    for i in range(3):
        ok = mag_op_zon_starten()
        if DEBUG == 1:
            log.info(f"Boiler debug | start_validatie stap={i+1}/3 | mag_op_zon_starten={ok}")
        if not ok:
            return False
        await task.sleep(5)

    ok = mag_op_zon_starten()
    if DEBUG == 1:
        log.info(f"Boiler debug | start_validatie eindcontrole | mag_op_zon_starten={ok}")
    return ok


# Start de boiler en laat de timer lopen met de nog resterende opwarmtijd.
def boiler_start(reden=""):
    service.call("switch", "turn_on", entity_id="switch.boiler_stopcontact_1")
    service.call("timer", "start", entity_id="timer.boiler_opwarmtijd")
    log_boiler("Start laden", reden)


# Stopt de boiler gecontroleerd.
def boiler_stop(reden=""):
    if state.get("timer.boiler_opwarmtijd") == "active":
        service.call("timer", "pause", entity_id="timer.boiler_opwarmtijd")
    elif state.get("timer.boiler_opwarmtijd") == "idle":
        service.call("input_boolean", "turn_on", entity_id="input_boolean.boiler_al_verwarmd")

    service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")
    log_boiler("Stop laden", reden)


# Start de boiler op zonne-overschot zodra alle voorwaarden 30 seconden
# aaneengesloten waar zijn.
@state_trigger(
    "sensor.p1_meter_power not in ['unknown', 'unavailable', None] and "
    "sensor.nextenergy_bms_soc not in ['unknown', 'unavailable', None] and "
    f"float(sensor.p1_meter_power) <= {START_TERUGLEVERING_W} and "
    "float(sensor.nextenergy_bms_soc) >= 70 and "
    "input_boolean.boiler_al_verwarmd == 'off' and "
    "switch.boiler_stopcontact_1 == 'off' and "
    "timer.boiler_opwarmtijd == 'paused'",
    state_hold=30
)
async def _start_op_zon():
    if datetime.now().time() >= time(15, 0):
        return

    if not await start_validatie():
        if DEBUG == 1:
            log_boiler("Start afgewezen", "voorwaarden niet stabiel gebleven tijdens extra validatie")
        return

    try:
        p1 = float(state.get("sensor.p1_meter_power"))
        soc = float(state.get("sensor.nextenergy_bms_soc"))
        boiler_start(f"zonneladen; p1={p1:.0f}W, soc={soc:.0f}%")
    except (TypeError, ValueError):
        boiler_start("zonneladen")


# Stopt de boiler zodra tijdens zonneladen de netafname 30 seconden
# aaneengesloten boven de ingestelde stopdrempel ligt.
@state_trigger(
    "sensor.p1_meter_power not in ['unknown', 'unavailable', None] and "
    f"float(sensor.p1_meter_power) >= {STOP_NETAFNAME_W} and "
    "switch.boiler_stopcontact_1 == 'on'",
    state_hold=30
)
def _stop_op_netafname():
    if datetime.now().time() >= time(15, 0):
        return

    try:
        p1 = float(state.get("sensor.p1_meter_power"))
        boiler_stop(f"netafname te hoog; p1={p1:.0f}W")
    except (TypeError, ValueError):
        boiler_stop("netafname te hoog")


# Reset elke ochtend de boilerlogica.
@time_trigger("cron(0 6 * * *)")
async def _reset_0600():
    service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")
    await task.sleep(2)

    service.call("input_boolean", "turn_off", entity_id="input_boolean.boiler_al_verwarmd")
    service.call("timer", "start", entity_id="timer.boiler_opwarmtijd", duration=DAG_TIMER)
    await task.sleep(1)
    service.call("timer", "pause", entity_id="timer.boiler_opwarmtijd")

    log_boiler("Dagreset uitgevoerd", "timer op 30 minuten gezet en gepauzeerd")


# Handelt het moment af waarop de timer volledig is afgelopen.
@event_trigger("timer.finished")
def _timer_klaar(**kwargs):
    if (kwargs.get("data") or {}).get("entity_id") != "timer.boiler_opwarmtijd" and kwargs.get("entity_id") != "timer.boiler_opwarmtijd":
        return

    service.call("input_boolean", "turn_on", entity_id="input_boolean.boiler_al_verwarmd")
    service.call("switch", "turn_off", entity_id="switch.boiler_stopcontact_1")
    log_boiler("Timer klaar", "daglimiet bereikt")


# Start om 15:00 alsnog de boiler via het net als hij nog niet klaar is.
@time_trigger("cron(0 15 * * *)")
def _forced_1500():
    if state.get("binary_sensor.bewoond") != "on":
        log_boiler("15:00-run overgeslagen", "woning niet bewoond")
        return
    if state.get("input_boolean.boiler_al_verwarmd") != "off":
        log_boiler("15:00-run overgeslagen", "boiler al verwarmd")
        return
    if state.get("switch.boiler_stopcontact_1") != "off":
        log_boiler("15:00-run overgeslagen", "boiler stond al aan")
        return
    if state.get("timer.boiler_opwarmtijd") != "paused":
        log_boiler("15:00-run overgeslagen", "timer niet in paused-status")
        return

    boiler_start("geforceerde 15:00-run")


# Herstelt logisch gedrag na een Home Assistant herstart.
@event_trigger("homeassistant_started")
async def _ha_start(event_name=None, data=None, kwargs=None):
    await task.sleep(30)

    if datetime.now().time() < time(15, 0):
        if state.get("switch.boiler_stopcontact_1") == "on":
            try:
                p1 = float(state.get("sensor.p1_meter_power"))
            except (TypeError, ValueError):
                p1 = None

            if p1 is not None and p1 >= STOP_NETAFNAME_W:
                boiler_stop(f"na herstart; netafname te hoog; p1={p1:.0f}W")

        elif mag_op_zon_starten():
            try:
                p1 = float(state.get("sensor.p1_meter_power"))
                soc = float(state.get("sensor.nextenergy_bms_soc"))
                boiler_start(f"na herstart; zonneladen; p1={p1:.0f}W, soc={soc:.0f}%")
            except (TypeError, ValueError):
                boiler_start("na herstart; zonneladen")


# Logt elke minuut de relevante toestand als DEBUG aan staat,
# maar alleen wanneer de woning bewoond is en alleen tussen 10:00 en 15:00.
@time_trigger("cron(* 10-14 * * *)")
def _debug_boiler_status():
    if DEBUG != 1:
        return
    if state.get("binary_sensor.bewoond") != "on":
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    p1_raw = state.get("sensor.p1_meter_power")
    soc_raw = state.get("sensor.nextenergy_bms_soc")
    boiler = state.get("switch.boiler_stopcontact_1")
    timer_state = state.get("timer.boiler_opwarmtijd")
    al_verwarmd = state.get("input_boolean.boiler_al_verwarmd")

    try:
        p1 = float(p1_raw)
    except (TypeError, ValueError):
        p1 = None

    try:
        soc = float(soc_raw)
    except (TypeError, ValueError):
        soc = None

    voor_1500 = datetime.now().time() < time(15, 0)
    p1_ok = p1 is not None and p1 <= START_TERUGLEVERING_W
    soc_ok = soc is not None and soc >= 70
    timer_ok = timer_state == "paused"
    boiler_ok = boiler == "off"
    dag_ok = al_verwarmd == "off"

    start_ok = voor_1500 and p1_ok and soc_ok and timer_ok and boiler_ok and dag_ok

    log.info(
        "Boiler debug | "
        f"ts={now} | "
        f"p1={p1_raw} | "
        f"soc={soc_raw} | "
        f"boiler={boiler} | "
        f"timer={timer_state} | "
        f"al_verwarmd={al_verwarmd} | "
        f"voor_1500={voor_1500} | "
        f"p1_ok={p1_ok} | "
        f"soc_ok={soc_ok} | "
        f"timer_ok={timer_ok} | "
        f"boiler_ok={boiler_ok} | "
        f"dag_ok={dag_ok} | "
        f"start_ok={start_ok}"
    )
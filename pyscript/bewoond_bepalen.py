# bewoond_bepalen.py (Pyscript)
# -------------------------------------------------------------------
# Dag-latch "iPhone vandaag gezien" (met vakantie-uitzondering)
#
# Doel:
# - Per kalenderdag éénmalig vastleggen dat Arnaud (via iPhone) thuis is geweest.
# - De latch (input_boolean) wordt gebruikt als dag-indicator:
#   "Arnaud is vandaag minstens één keer thuis gezien".
#
# Gedrag:
# 1) Bij detectie van iPhone = home:
#    - Zet de latch aan als deze nog uit staat.
#    - Dit gebeurt alleen buiten vakantie.
#    - Meerdere 'home'-events op dezelfde dag hebben geen effect.
#
# 2) Daggrens (00:00):
#    - Elke nacht wordt de latch gereset naar 'off'.
#    - Als de iPhone op dat moment al thuis is,
#      wordt de latch direct weer aangezet (nieuwe dag),
#      behalve tijdens vakantie.
#
# 3) Vakantie-logica:
#    - Bij vakantie = aan: latch altijd uit (logica uitgeschakeld).
#    - Bij vakantie = uit:
#      - Als de iPhone al thuis is, wordt de latch direct opnieuw gezet.
#
# Ontwerpprincipes:
# - Dag-semantiek i.p.v. moment-semantiek
# - Idempotent: meerdere triggers veroorzaken geen bijwerkingen
# - Robuust bij aaneengesloten thuisblijven
# - Vakantie is een harde override
#
# Geschikt als bouwsteen voor:
# - aanwezigheid per dag
# - dag-/nacht-automatiseringen
# - energie- en comfortlogica
# - "eerste keer vandaag"-meldingen
# -------------------------------------------------------------------

PHONE = "device_tracker.iphone13arnaud"
LATCH = "input_boolean.iphone_vandaag_gezien"
VAKANTIE = "input_boolean.vakantie"

from datetime import datetime, time as dtime

def _after_11():
    """True als het 11:00 of later is."""
    return datetime.now().time() >= dtime(11, 0)



def _set_latch_on_if_phone_home_after_11():
    """Zet latch aan als telefoon thuis is én het 11:00 of later is."""
    if state.get(VAKANTIE) == "on":
        return

    if not _after_11():
        return

    if state.get(PHONE) == "home" and state.get(LATCH) != "on":
        service.call("input_boolean", "turn_on", entity_id=LATCH)


@state_trigger(PHONE)
def iphone_arnaud_eenkeer_gezien():
    """
    Zodra iPhone Arnaud thuis is gedetecteerd,
    zet de dag-latch alleen aan als het 11:00 of later is
    (behalve tijdens vakantie).
    """
    if state.get(PHONE) == "home":
        _set_latch_on_if_phone_home_after_11()


@time_trigger("cron(0 11 * * *)")
def zet_latch_om_1100_als_iphone_thuis_is():
    """
    Elke dag om 11:00:
    als de iPhone dan al thuis is, zet de latch aan.
    Zo werkt het ook wanneer je de hele ochtend al thuis bent.
    """
    _set_latch_on_if_phone_home_after_11()


@time_trigger("cron(0 0 * * *)")
def reset_iphone_vandaag_gezien_middernacht():
    """
    Elke nacht om 00:00: reset de dag-latch naar off.
    Let op: we zetten hem NIET direct weer aan als je al thuis bent,
    want dat mag pas vanaf 11:00.
    """
    service.call("input_boolean", "turn_off", entity_id=LATCH)


@state_trigger(f"{VAKANTIE} == 'on'")
def vakantie_aangezet_reset_latch():
    """Bij vakantie aan: latch altijd uit."""
    service.call("input_boolean", "turn_off", entity_id=LATCH)


@state_trigger(f"{VAKANTIE} == 'off'")
def vakantie_uit_herbereken_latch():
    """
    Als vakantie uit gaat:
    zet latch alleen aan als het 11:00 of later is én je bent thuis.
    """
    _set_latch_on_if_phone_home_after_11()

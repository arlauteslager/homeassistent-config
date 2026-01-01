# /config/pyscript/test.py
#
# Testscript:
# - Elke 5 minuten
# - Stuurt een melding met tekst: "py test"

# ------------------------------------------------------------
# CRON UITLEG (pyscript / Home Assistant)
#
# Syntax:
#   cron(minuut uur dag-van-maand maand dag-van-week)
#
# Betekenis per veld:
#   minuut        0–59
#   uur           0–23
#   dag-van-maand 1–31
#   maand         1–12
#   dag-van-week  0–6  (0 = maandag, 6 = zondag)
#
# Speciale tekens:
#   *      = elke mogelijke waarde
#   */5    = elke 5 eenheden
#   0,30   = meerdere vaste waarden
#
# Voorbeelden:
#   cron(0 7 * * *)        → elke dag om 07:00
#   cron(*/5 * * * *)      → elke 5 minuten
#   cron(0 0 * * 1)        → elke maandag om 00:00
#   cron(30 22 * * 5)      → elke vrijdag om 22:30
#
# In dit script:
#   cron(*/5 * * * *)      → elke 5 minuten
# ------------------------------------------------------------
# @time_trigger("cron(*/2 * * * *)")
# def py_test_message():
#     service.call(
#         "persistent_notification",
#         "create",
#         title="Pyscript test",
#         message="py test via cron jajaja",
#     )

# @service
# def py_test_now():
#     service.call(
#         "persistent_notification",
#         "create",
#         title="Pyscript test",
#         message="py test",
#     )

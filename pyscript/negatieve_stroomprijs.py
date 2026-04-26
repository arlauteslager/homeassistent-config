# /config/pyscript/negatieve_stroomprijs.py

@time_trigger("cron(1 * * * *)")
def check_negatieve_stroomprijs():
    prijs = float(state.get("sensor.enever_stroomprijs_nextenergy") or 0)

    if prijs < 0:
        service.call(
            "notify",
            "mobile_app_iphone_13_arnaud",
            title="Negatieve stroomprijs",
            message=f"De stroomprijs is nu negatief: €{prijs:.3f}/kWh"
        )

# /config/pyscript/boiler_negatieve_prijs.py

@time_trigger("cron(0 13 * * *)")
def boiler_aan_bij_negatieve_prijs():
    prijs = float(state.get("sensor.enever_stroomprijs_nextenergy") or 0)

    if prijs < -0.10:
        switch.turn_on(entity_id="switch.boiler_stopcontact_1")
        notify.mobile_app_jouw_telefoon(
            title="Boiler gestart",
            message=f"Boiler aangezet om 13:00. Stroomprijs: €{prijs:.3f}/kWh"
        )
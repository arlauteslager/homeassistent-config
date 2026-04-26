@time_trigger("cron(30 7 * * *)")
def wifi_werkkamer_aan():
    service.call("switch", "turn_on", entity_id="switch.slimme_stekker_voor_wifi_werkkamer")


@time_trigger("cron(0 22 * * *)")
def wifi_werkkamer_uit():
    service.call("switch", "turn_off", entity_id="switch.slimme_stekker_voor_wifi_werkkamer")
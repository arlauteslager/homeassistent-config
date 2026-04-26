# LED aan bij zonsondergang
@time_trigger("once(sunset)")
def aquarium_led_aan():
    switch.turn_on(entity_id="switch.led_aquarium_stopcontact_1")


# LED uit om 23:00
@time_trigger("cron(0 23 * * *)")
def aquarium_led_uit():
    switch.turn_off(entity_id="switch.led_aquarium_stopcontact_1")


# Luchtpomp aan om 14:00 en 02:00, daarna na 30 minuten weer uit
@time_trigger("cron(0 14 * * *)")
@time_trigger("cron(0 2 * * *)")
def aquarium_luchtpomp_cyclus():
    switch.turn_on(entity_id="switch.air_aquarium_stopcontact_1")
    task.sleep(90 * 60)
    switch.turn_off(entity_id="switch.air_aquarium_stopcontact_1")


# Waterpomp elk heel uur aan van 23:00 t/m 15:00, daarna na 5 minuten weer uit
@time_trigger("cron(0 23,0-15 * * *)")
def aquarium_waterpomp_cyclus():
    switch.turn_on(entity_id="switch.aqua_waterpomp")
    task.sleep(5 * 60)
    switch.turn_off(entity_id="switch.aqua_waterpomp")
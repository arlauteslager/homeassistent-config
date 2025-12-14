- id: welkom_thuis_kinderen_sonos
  alias: Welkom-thuis bericht op Sonos bij binnenkomst (wifi presence)
  trigger:
    - platform: state
      entity_id:
        - device_tracker.iphone_olin
        - device_tracker.iphone_jinke
        - device_tracker.iphone_arnaud
#        - device_tracker.iphone15_marjolein
        - device_tracker.iphone13arnaud
        - device_tracker.iphone_arnaud
#        - device_tracker.iphone
#        - device_tracker.mac_mini
      from: 'not_home'
      to: 'home'
  condition:
    # Anti-spam: alleen overdag/avond (pas aan naar smaak)
    - condition: time
      after: '07:00:00'
      before: '21:30:00'
  action:
    # 1) Bepaal wie er binnenkomt
    - variables:
        binnenkomer: >
          {% if trigger.entity_id.endswith('jinke') %}Jinke
          {% elif trigger.entity_id.endswith('olin') %}Olin
          {% elif trigger.entity_id.endswith('arnaud') %}Arnaud
          {% elif trigger.entity_id.endswith('marjolein') %}Marjolein
          {% elif trigger.entity_id.endswith('mini') %}MacMini
          {% else %}iemand{% endif %}

        selected_entity: >
          sensor.joke

        # Welke bron gebruiken we?
#        bron: >
#          {% if trigger.entity_id.endswith('jinke') or trigger.entity_id.endswith('olin') %}
#            joke
#          {% elif trigger.entity_id.endswith('marjolein') %}
#            joke
#          {% else %}
#            niets
#          {% endif %}

    # 2) Bepaal bijbehorende sensor-entity
#    - variables:
#        selected_entity: >
#          {% if bron == 'joke' %}
#            sensor.joke
#          {% else %}
#            sensor.joke
#          {% endif %

    # 3) Haal alleen deze sensor nu op
    - service: homeassistant.update_entity
      data:
        entity_id: "{{selected_entity}}"

    # 4) Wacht tot er een bruikbare waarde is (max 5 sec)
    - wait_template: "{{ states(selected_entity) not in ['unknown', 'unavailable', ''] }}"
      timeout: "00:00:15"
      continue_on_timeout: true

    # 5) Tekst uit de juiste sensor halen (met fallback)
    - variables:
        tekst: >
          {% set v = states(selected_entity) %}
          {% if v in ['unknown', 'unavailable', ''] %}
            Ik heb nu even geen tekst voor je.
          {% else %}
            {{ v }}
          {% endif %}

    - service: openai_conversation.conversation
      data:
        # pas assistant_name aan als jij een andere hebt ingesteld
        assistant: default
        prompt: >
          Vertaal deze Engelse mop naar natuurlijk, vlot Nederlands.
          Maak er één lopende mop van zonder extra tekst ervoor of erna, met de clou op het eind zodat je er om moet lachen. Let bij het vertalen op dat de nederlandse vertaling nog steeds een clou heeft en grappig is.
          Mop: "{{ tekst }}"
      response_variable: antwoord_ai

    - service: script.tts_with_smart_volume
      data:
        player: media_player.achterkamer
        text: "Héé {{ binnenkomer }}!, je bent er. Ken je deze al? ,,, {{ antwoord_ai['response'] }}"
        volume: 0.25

    - service: logbook.log
      data:
        name: "HOME"
        message: "Héé {{ binnenkomer }}"
    
  mode: parallel

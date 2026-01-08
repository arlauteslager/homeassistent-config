# /config/pyscript/testmelding.py
# Test: maak een persistent notification aan

@service
def test_melding():
    """Handmatig aanroepen: pyscript.test_melding"""
    service.call(
        "notify",
        "mobile_app_iphone_13_arnaud",
        title="Testmelding",
        message="Dit is een pushmelding op je iPhone via Home Assistant.",
    )

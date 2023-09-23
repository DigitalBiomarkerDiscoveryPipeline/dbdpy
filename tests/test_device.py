from dbdpy import device


def test_get_device_info():
    dev = device.CommercialDevice("Apple Watch", "Series 9")
    assert dev.get_device_info() == "Apple Watch - Series 9"


def test_ha_device_info():
    dev = device.CommercialDevice("Apple Watch", "Series 9")
    assert dev.get_device_info() == "Apple Watch - Series 9"

import pytest
from dbdpy import device


def test_get_device_info():
    dev = device.CommercialDevice("Apple Watch", "Series 9")
    assert dev.get_device_info() == "Apple Watch - Series 9"


# @pytest.mark.parametrize(
#     "brand, age, is_damaged, expected",
#     [
#         ("Apple", 1, False, 800),
#         ("Apple", 2, False, 640),
#         ("Fitbit", 1, False, 850),
#     ],
# )
# def test_calculate_rescale_value(brand, age, is_damaged, expected):
#     dev = device.CommercialDevice(brand, "AnyModel")
#     assert dev.calculate_rescale_value(age, is_damaged) == expected


@pytest.mark.parametrize(
    "brand, age, is_damaged, expected",
    [
        ("Apple", 1, False, 800),
        ("Apple", 2, False, 640),
        ("Fitbit", 1, False, 850),
    ],
)
def test_calculate_rescale_value(brand, age, is_damaged, expected):
    dev = device.CommercialDevice(brand, "AnyModel")
    assert dev.calculate_rescale_value(age, is_damaged) == expected

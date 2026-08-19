from plant_watering import plant_watering

def test_plant_watering():
    result = plant_watering.invoke({})
    assert result is True
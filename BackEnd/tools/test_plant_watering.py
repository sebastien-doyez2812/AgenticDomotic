from plant_watering import plant_watering
from unittest.mock import patch, MagicMock

@patch('plant_watering.socket.socket')
def test_plant_watering(mock_socket_class):
    mock_socket_instance = MagicMock()
    mock_socket_class.return_value = mock_socket_instance
    result = plant_watering.invoke({})
    assert result is True

    mock_socket_instance.connect.assert_called_once_with(("192.168.2.14", 1234))
    mock_socket_instance.sendall.assert_called_once_with(b'\x01')
    mock_socket_instance.close.assert_called_once()
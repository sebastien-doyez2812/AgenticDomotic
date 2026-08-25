import socket
from langchain_core.tools import tool

# TODO
IP_ADDRESS="192.168.2.14"
PORT= 1234


@tool
def plant_watering():
    """
    Function to simulate plant watering.
    """

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP_ADDRESS, PORT))

        s.sendall(b'\x01') # Sending 1 bit to say plant needs water!
        s.close()
        return True
        
    except Exception as e:
        print(f"An error occurred while watering the plants: {e}")
        return False

if __name__ == "__main__":
    # Test the plant_watering function
    result = plant_watering.invoke({})
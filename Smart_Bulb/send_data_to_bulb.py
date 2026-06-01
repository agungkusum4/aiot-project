from tuya_connector import TuyaOpenAPI
import time

# =========================
# TUYA CONFIG
# =========================
ACCESS_ID = "rwh7a5ekwwhkshf9gxjg"
ACCESS_SECRET = "e781145309b04b83a62926e02eb9c42f"
DEVICE_ID = "a3523d565ec3f824d3w3ko"

API_ENDPOINT = "https://openapi-sg.iotbing.com"

# =========================
# CONNECT TUYA
# =========================

openapi = TuyaOpenAPI(
    API_ENDPOINT,
    ACCESS_ID,
    ACCESS_SECRET
)

openapi.connect()

print("Bulb Connected!")

# =========================
# FUNCTION SEND TO BULB
# =========================

def send_to_bulb(ai_output):

    # =====================
    # AC OFF
    # =====================

    if ai_output == "OFF":

        commands_off = {
            "commands": [
                {
                    "code": "switch_led",
                    "value": False
                }
            ]
        }

        response = openapi.post(
            f"/v1.0/iot-03/devices/{DEVICE_ID}/commands",
            commands_off
        )

        print("AC OFF")
        print(response)

    # =====================
    # AC ON + SET TEMP
    # =====================

    else:

        # Convert suhu -> brightness
        brightness = int(ai_output) * 10

        # STEP 1 -> ON bulb
        commands_on = {
            "commands": [
                {
                    "code": "switch_led",
                    "value": True
                },
                {
                    "code": "work_mode",
                    "value": "white"
                }
            ]
        }

        openapi.post(
            f"/v1.0/iot-03/devices/{DEVICE_ID}/commands",
            commands_on
        )

        print("Bulb ON")

        # Delay supaya automation stabil
        time.sleep(2)

        # STEP 2 -> set brightness
        commands_brightness = {
            "commands": [
                {
                    "code": "bright_value_v2",
                    "value": brightness
                }
            ]
        }

        response = openapi.post(
            f"/v1.0/iot-03/devices/{DEVICE_ID}/commands",
            commands_brightness
        )

        print(f"Set AC -> {ai_output}°C")
        print(f"Brightness -> {brightness}")
        print(response)
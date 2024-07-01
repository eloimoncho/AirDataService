import json
import paho.mqtt.client as mqtt
import requests

def handle_mqtt_message(message, client):
    print('handle_mqtt_message:', message)
    splited = message.topic.split("/")
    origin = splited[0]
    command = splited[2]
    sending_topic = mqtt_topic + "/" + origin
    print('command:', command)
    if command == "add_flightplan":
        headers = {"Content-Type": "application/json"}
        print('preResponse')
        data_json = json.loads(message.payload.decode())
        response = requests.post(
            'http://localhost:9000/add_flightplan', json=data_json, headers=headers
        )
        print('postResponse', response)
        print('response.json', response.json)
        if response.status_code == 200:
            response_json = response.json()
            print('response.json', response_json)
            flightplan_id_ground = response_json.get("id")
            client.publish(sending_topic + "/add_flightplan", json.dumps(response_json))
            if response_json.get("success", False):
                print('GOOD response.json:', response_json)
            else:
                print('BAD response.json:', response_json)
        else:
            print('HTTP Error:', response.status_code)
    elif command == "get_flight_plan":
        flightPlan_title = message.payload
        print('message.payload', flightPlan_title)
        response_json = requests.get('http://localhost:9000/get_flight_plan/' + flightPlan_title).json()
        client.publish(sending_topic + "/get_flight_plan", json.dumps(response_json))
    elif command == "add_flight":
        headers = {"Content-Type": "application/json"}
        data_json = json.loads(message.payload.decode())
        response = requests.post('http://localhost:9000/add_flight', json=data_json, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            print('response.json', response_json)
            client.publish(sending_topic + "/add_flight", json.dumps(response_json))
            if response_json.get("success", False):
                print('GOOD response.json:', response_json)
            else:
                print('BAD response.json:', response_json)
        else:
            print('HTTP Error:', response.status_code)
    elif command == "get_all_flights":
        response = requests.get('http://localhost:9000/get_all_flights').json()
        print("RESPONSE: \n", response)
        response_json = response.json()
        client.publish(sending_topic + "/get_all_flights", json.dumps(response_json))
    elif command == "get_all_flightPlans":
        response = requests.get('http://localhost:9000/get_all_flightPlans').json()
        print("RESPONSE: \n", response)
        client.publish(sending_topic + "/get_all_flightPlans", json.dumps(response))
        print(sending_topic + "/get_all_flightPlans")
    elif command == "get_pictures":
        file_name = message.payload
        response = requests.get('http://localhost:9000/get_pictures/'+ {file_name}).json()
        response_json = response.json()
        client.publish(sending_topic + "/get_pictures", json.dumps(response_json))
    else:
        print("No entiendo el mensaje")

def on_message(client, userdata, message):
    print("Mensaje recibido: " + message.payload.decode())
    # Analizar el mensaje recibido y realizar la solicitud HTTP correspondiente
    handle_mqtt_message(message, client)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connection OK")
    else:
        print("Bad connection")

# Configuración de MQTT
#mqtt_broker_address = "broker.hivemq.com"  # Dirección del broker MQTT
#mqtt_port = 8000  # Puerto del broker MQTT
mqtt_topic = "airDataService"  # Tópico al que se publicarán los mensajes
client = mqtt.Client("AirDataService", transport="websockets")
client.on_connect = on_connect
client.on_message = on_message
# Conexión al broker MQTT
client.username_pw_set("dronsEETAC", "mimara1456.")
client.connect("classpip.upc.edu", 8000)
#client.connect(mqtt_broker_address, mqtt_port)
client.subscribe("+/airDataService/#", 2)
# Bucle principal para mantener la conexión y procesar los mensajes
client.loop_forever()

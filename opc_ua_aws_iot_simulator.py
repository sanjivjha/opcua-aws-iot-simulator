# File: opc_ua_aws_iot_simulator.py

import asyncio
import json
import time
import random
from asyncua import Server, Client, ua
from awscrt import mqtt
from awsiot import mqtt_connection_builder
import datetime

# Load configuration
def load_config():
    with open("aws_iot_config.json", "r") as config_file:
        return json.load(config_file)

CONFIG = load_config()

# Simulator Configuration
SIMULATOR_URL = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
SIMULATOR_NAMESPACE = "OPCUA_SIMULATION_SERVER"
LOCAL_UPDATE_INTERVAL = 1  # seconds
CLOUD_PUBLISH_INTERVAL = 5  # seconds

# AWS IoT Core Configuration
AWS_IOT_ENDPOINT = CONFIG["aws_iot_endpoint"]
AWS_IOT_CLIENT_ID = CONFIG["client_id"]
AWS_IOT_CERT_PATH = CONFIG["cert_path"]
AWS_IOT_KEY_PATH = CONFIG["key_path"]
AWS_IOT_ROOT_CA_PATH = CONFIG["root_ca_path"]
AWS_IOT_TOPIC = CONFIG["topic"]

class OPCUASimulator:
    def __init__(self, url=SIMULATOR_URL):
        self.url = url
        self.server = Server()
        self.temperature_node = None
        self.pressure_node = None

    async def init(self):
        await self.server.init()
        self.server.set_endpoint(self.url)
        
        uri = SIMULATOR_NAMESPACE
        self.idx = await self.server.register_namespace(uri)
        
        objects = self.server.get_objects_node()
        self.system = await objects.add_object(self.idx, "SimulationSystem")
        
        self.temperature_node = await self.system.add_variable(self.idx, "Temperature", 20.0)
        self.pressure_node = await self.system.add_variable(self.idx, "Pressure", 1.0)
        
        await self.temperature_node.set_writable()
        await self.pressure_node.set_writable()

    async def start(self):
        await self.server.start()
        print(f"OPC-UA Simulator server started at {self.url}")

    async def update_values(self):
        while True:
            temperature = 20 + random.uniform(-5, 5)
            pressure = 1 + random.uniform(-0.1, 0.1)
            
            await self.temperature_node.write_value(temperature)
            await self.pressure_node.write_value(pressure)
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Local sensor data updated: Temperature = {temperature:.2f}°C, Pressure = {pressure:.2f} bar")
            
            await asyncio.sleep(LOCAL_UPDATE_INTERVAL)

    def get_node_ids(self):
        return {
            "temperature": self.temperature_node.nodeid.to_string(),
            "pressure": self.pressure_node.nodeid.to_string()
        }

class AWSIoTInterface:
    def __init__(self):
        self.mqtt_connection = None

    def connect(self):
        try:
            self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=AWS_IOT_ENDPOINT,
                cert_filepath=AWS_IOT_CERT_PATH,
                pri_key_filepath=AWS_IOT_KEY_PATH,
                ca_filepath=AWS_IOT_ROOT_CA_PATH,
                client_id=AWS_IOT_CLIENT_ID,
                clean_session=False,
                keep_alive_secs=30
            )
            connect_future = self.mqtt_connection.connect()
            connect_future.result()
            print("Connected to AWS IoT Core")
        except Exception as e:
            print(f"Failed to connect to AWS IoT Core: {e}")
            self.mqtt_connection = None

    def publish(self, message):
        if self.mqtt_connection:
            self.mqtt_connection.publish(
                topic=AWS_IOT_TOPIC,
                payload=json.dumps(message),
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Data published to AWS IoT Core: {message}")
        else:
            print("MQTT connection not established. Message not published.")

    def disconnect(self):
        if self.mqtt_connection:
            disconnect_future = self.mqtt_connection.disconnect()
            disconnect_future.result()
            print("Disconnected from AWS IoT Core")
        else:
            print("No active MQTT connection to disconnect.")

async def main():
    print("Starting OPC-UA to AWS IoT Core Simulator...")
    print(f"Local sensor update interval: {LOCAL_UPDATE_INTERVAL} seconds")
    print(f"Cloud publish interval: {CLOUD_PUBLISH_INTERVAL} seconds")
    
    simulator = OPCUASimulator()
    await simulator.init()
    await simulator.start()
    
    asyncio.create_task(simulator.update_values())
    
    aws_iot = AWSIoTInterface()
    aws_iot.connect()
    
    node_ids = simulator.get_node_ids()
    
    print(f"Simulator is running. Publishing to AWS IoT Core topic: {AWS_IOT_TOPIC}")
    print("Press Ctrl+C to stop the simulator.")
    
    async with Client(url=SIMULATOR_URL) as client:
        while True:
            try:
                temperature_node = client.get_node(node_ids["temperature"])
                pressure_node = client.get_node(node_ids["pressure"])
                
                temperature = await temperature_node.read_value()
                pressure = await pressure_node.read_value()
                
                message = {
                    "timestamp": time.time(),
                    "temperature": round(temperature, 2),
                    "pressure": round(pressure, 2)
                }
                aws_iot.publish(message)
                
                await asyncio.sleep(CLOUD_PUBLISH_INTERVAL)
            except Exception as e:
                print(f"Error occurred: {e}")
                await asyncio.sleep(CLOUD_PUBLISH_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    finally:
        AWSIoTInterface().disconnect()
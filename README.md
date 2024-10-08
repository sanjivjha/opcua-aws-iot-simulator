# OPC-UA to AWS IoT Core Simulator

This project simulates an OPC-UA server that generates sensor data, aggregates it, and publishes it to AWS IoT Core. It's designed to demonstrate the integration between OPC-UA systems and AWS IoT, which is common in industrial IoT scenarios.

## Features

- Simulates an OPC-UA server generating temperature and pressure data
- Aggregates data over configurable intervals before publishing
- Connects to AWS IoT Core and publishes aggregated data
- Provides a setup script for easy AWS IoT configuration
- Simulates realistic sensor behavior with frequent local updates and less frequent cloud publishing

## Prerequisites

- Python 3.7+
- AWS account with IoT Core access
- AWS CLI configured with appropriate credentials

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/opcua-aws-iot-simulator.git
   cd opcua-aws-iot-simulator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### 1. AWS IoT Setup

Run the AWS IoT setup script:
```
python aws_iot_setup.py
```

This script does the following:
- Creates an IoT Thing in your AWS account
- Creates a policy for the Thing
- Generates and attaches a certificate to the Thing
- Downloads the necessary certificates and keys
- Creates a configuration file (`aws_iot_config.json`) with all required details

You'll be prompted to enter:
- A name for your IoT Thing
- A topic name for publishing messages

### 2. Run the Simulator

After setup, run the simulator:
```
python opc_ua_aws_iot_simulator.py
```

This script:
- Starts an OPC-UA server that simulates sensor data (temperature and pressure)
- Aggregates the data over the specified interval
- Publishes the aggregated data to AWS IoT Core

## Configuration

### AWS IoT Configuration

The `aws_iot_config.json` file contains the AWS IoT Core configuration. It's automatically generated by the setup script, but you can create or modify it manually if needed. The file structure is:

```json
{
  "aws_iot_endpoint": "your-iot-endpoint.iot.your-region.amazonaws.com",
  "client_id": "your-thing-name",
  "topic": "your/topic/name",
  "cert_path": "path/to/certificate.pem.crt",
  "key_path": "path/to/private.pem.key",
  "root_ca_path": "path/to/AmazonRootCA1.pem"
}
```

### Simulator Configuration

You can adjust the following parameters in `opc_ua_aws_iot_simulator.py`:

- `LOCAL_UPDATE_INTERVAL`: Frequency of local sensor data updates (in seconds)
- `CLOUD_PUBLISH_INTERVAL`: Frequency of publishing aggregated data to AWS IoT Core (in seconds)

### Data Aggregation

The simulator aggregates data over the `CLOUD_PUBLISH_INTERVAL`. To modify the aggregation method:

1. Locate the `get_aggregated_data()` method in the `OPCUASimulator` class.
2. Modify the aggregation logic as needed. Currently, it calculates the average.

Example of changing to max value instead of average:

```python
def get_aggregated_data(self):
    max_temperature = max(self.temperature_data) if self.temperature_data else 0
    max_pressure = max(self.pressure_data) if self.pressure_data else 0
    return round(max_temperature, 2), round(max_pressure, 2)
```

## Adapting to Real Sensors

To adapt this simulator to work with actual sensors in a real environment:

1. OPC-UA Server Connection:
   - Replace the `OPCUASimulator` class with a connection to your real OPC-UA server.
   - Update the `SIMULATOR_URL` to point to your actual OPC-UA server address.

2. Node IDs:
   - In the `get_node_ids()` method, replace the simulated node IDs with the actual node IDs from your OPC-UA server.

3. Data Reading:
   - Modify the `update_values()` method to read real data from your OPC-UA server instead of generating random values.

4. Error Handling:
   - Implement robust error handling for network issues, sensor failures, etc.

5. Security:
   - Ensure proper security measures are in place, including secure communication with the OPC-UA server and AWS IoT Core.

6. Testing:
   - Thoroughly test the system in a non-production environment before deploying.

7. Monitoring:
   - Implement monitoring and alerting for the data collection and publication process.

8. Scaling:
   - Consider how the solution will scale with multiple sensors or higher data frequencies.

Example of reading from a real OPC-UA server:

```python
async def update_values(self):
    async with Client(url=self.url) as client:
        temp_node = client.get_node("ns=2;s=Temperature")
        pressure_node = client.get_node("ns=2;s=Pressure")
        while True:
            temperature = await temp_node.read_value()
            pressure = await pressure_node.read_value()
            self.temperature_data.append(temperature)
            self.pressure_data.append(pressure)
            await asyncio.sleep(LOCAL_UPDATE_INTERVAL)
```

## Contributing

We welcome contributions to improve this simulator! Here are some ways you can contribute:

1. Report bugs or suggest features by opening issues
2. Improve documentation
3. Add new features or fix bugs by submitting pull requests

To contribute code:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with clear, descriptive messages
4. Push your changes to your fork
5. Submit a pull request to the main repository

Please ensure your code adheres to the existing style and includes appropriate tests and documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [AsyncUA](https://github.com/FreeOpcUa/asyncua) for the OPC-UA implementation
- [AWS IoT Device SDK](https://github.com/aws/aws-iot-device-sdk-python-v2) for AWS IoT Core connectivity

## Disclaimer

This simulator is for demonstration purposes only and should not be used in production environments without proper security measures and testing.

# opcua-aws-iot-simulator
# OPC-UA to AWS IoT Core Simulator

This project simulates an OPC-UA server that generates sensor data and publishes it to AWS IoT Core. It's designed to demonstrate the integration between OPC-UA systems and AWS IoT, which is common in industrial IoT scenarios.

## Features

- Simulates an OPC-UA server generating temperature and pressure data
- Connects to AWS IoT Core and publishes data at configurable intervals
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

1. Run the AWS IoT setup script:
   ```
   python aws_iot_setup.py
   ```
   Follow the prompts to create your IoT thing and policy.

2. Run the simulator:
   ```
   python opc_ua_aws_iot_simulator.py
   ```

The simulator will start generating local sensor data and publishing to AWS IoT Core at the configured intervals.

## Configuration

You can adjust the following parameters in `opc_ua_aws_iot_simulator.py`:

- `LOCAL_UPDATE_INTERVAL`: Frequency of local sensor data updates (in seconds)
- `CLOUD_PUBLISH_INTERVAL`: Frequency of publishing to AWS IoT Core (in seconds)

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

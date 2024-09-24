# File: aws_iot_setup.py

import boto3
import json
import os
import requests

def create_thing(iot_client, thing_name):
    try:
        response = iot_client.create_thing(thingName=thing_name)
        return response['thingArn']
    except iot_client.exceptions.ResourceAlreadyExistsException:
        print(f"Thing '{thing_name}' already exists. Using the existing thing.")
        response = iot_client.describe_thing(thingName=thing_name)
        return response['thingArn']

def create_keys_and_certificate(iot_client):
    response = iot_client.create_keys_and_certificate(setAsActive=True)
    return response['certificateArn'], response['certificatePem'], response['keyPair']['PrivateKey']

def create_or_get_policy(iot_client, policy_name, topic):
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "iot:Publish",
                "iot:Connect"
            ],
            "Resource": [
                f"arn:aws:iot:*:*:topic/{topic}",
                "arn:aws:iot:*:*:client/${iot:Connection.Thing.ThingName}"
            ]
        }]
    }
    try:
        response = iot_client.create_policy(
            policyName=policy_name,
            policyDocument=json.dumps(policy_document)
        )
        print(f"Policy '{policy_name}' created successfully.")
        return response['policyArn']
    except iot_client.exceptions.ResourceAlreadyExistsException:
        print(f"Policy '{policy_name}' already exists. Using the existing policy.")
        response = iot_client.get_policy(policyName=policy_name)
        return response['policyArn']

def attach_policy_to_certificate(iot_client, policy_name, certificate_arn):
    iot_client.attach_policy(policyName=policy_name, target=certificate_arn)

def attach_thing_to_certificate(iot_client, thing_name, certificate_arn):
    iot_client.attach_thing_principal(thingName=thing_name, principal=certificate_arn)

def generate_config_file(thing_name, endpoint, topic, cert_path, key_path, root_ca_path):
    config = {
        "aws_iot_endpoint": endpoint,
        "client_id": thing_name,
        "topic": topic,
        "cert_path": cert_path,
        "key_path": key_path,
        "root_ca_path": root_ca_path
    }
    
    with open("aws_iot_config.json", "w") as config_file:
        json.dump(config, config_file, indent=2)

def download_root_ca():
    url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
    response = requests.get(url)
    if response.status_code == 200:
        with open("AmazonRootCA1.pem", "wb") as ca_file:
            ca_file.write(response.content)
        print("Root CA certificate downloaded successfully.")
        return "AmazonRootCA1.pem"
    else:
        print("Failed to download Root CA certificate.")
        return None

def main():
    thing_name = input("Enter the name for your IoT thing: ")
    policy_name = f"{thing_name}_policy"
    topic = input("Enter the topic name for publishing messages: ")

    iot_client = boto3.client('iot')

    print("Creating IoT Thing...")
    thing_arn = create_thing(iot_client, thing_name)

    print("Creating Keys and Certificate...")
    cert_arn, cert_pem, private_key = create_keys_and_certificate(iot_client)

    print("Creating or getting IoT Policy...")
    policy_arn = create_or_get_policy(iot_client, policy_name, topic)

    print("Attaching Policy to Certificate...")
    attach_policy_to_certificate(iot_client, policy_name, cert_arn)

    print("Attaching Thing to Certificate...")
    attach_thing_to_certificate(iot_client, thing_name, cert_arn)

    # Save the certificate and private key
    cert_path = f"{thing_name}_cert.pem"
    key_path = f"{thing_name}_private.key"
    with open(cert_path, "w") as cert_file:
        cert_file.write(cert_pem)
    with open(key_path, "w") as key_file:
        key_file.write(private_key)

    # Get the IoT endpoint
    endpoint = iot_client.describe_endpoint(endpointType='iot:Data-ATS')['endpointAddress']

    # Download Root CA certificate
    print("Downloading Root CA certificate...")
    root_ca_path = download_root_ca()

    if root_ca_path:
        # Generate config file
        generate_config_file(thing_name, endpoint, topic, cert_path, key_path, root_ca_path)

        print("\nSetup complete!")
        print(f"Thing Name: {thing_name}")
        print(f"Thing ARN: {thing_arn}")
        print(f"Certificate ARN: {cert_arn}")
        print(f"Policy ARN: {policy_arn}")
        print(f"IoT Endpoint: {endpoint}")
        print(f"Certificate saved as: {cert_path}")
        print(f"Private Key saved as: {key_path}")
        print(f"Root CA Certificate saved as: {root_ca_path}")
        print(f"Configuration saved as: aws_iot_config.json")
    else:
        print("Setup incomplete due to failure in downloading Root CA certificate.")

if __name__ == "__main__":
    main()
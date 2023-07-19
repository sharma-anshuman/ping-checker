import json
import sys
import time
from typing import Any
from csv import writer
import datetime as dt

from pythonping import ping

initial_data = {"devices_data": []}


def get_status() -> list:
    """
    This function pings the devices present in the device_data.json and gets the statuses of all devices

    :param:
        None
    :return:
        A list "status" having status of all the device in binary format i.e. 0 or 1
    """
    status = []
    try:
        with open('./device_data.json', 'r') as dataFile:
            data: Any = json.load(dataFile)
            for device in data['devices_data']:
                is_connected = list(ping(device['ip_address'], verbose=False, count=1))
                if str(is_connected[0]) == "Request timed out":
                    status.append(0)
                else:
                    status.append(1)
    except FileNotFoundError:
        with open('./device_data.json', 'a') as data_file:
            json.dump(initial_data, data_file, indent=2)
    return status


def update_csv(status: list) -> None:
    """
    This function updates the csv file using status list and devicedata.json

    param
        status:
    :return:
        None
    """
    try:
        with open('./device_data.json', 'r') as dataFile:
            data: Any = json.load(dataFile)
            status_csv: Any = open('./device_pings.csv', 'a')
            add_csv: Any = writer(status_csv)
            for idx, device in enumerate(data['devices_data']):
                add_csv.writerow([device["id"], device["device_name"], status[idx], dt.datetime.now().time()])
            status_csv.close()
    except FileNotFoundError:
        with open('./device_data.json', 'a') as data_file:
            json.dump(initial_data, data_file, indent=2)


def list_devices() -> None:
    """
    Prints all the data available in device_data.json
    :return:
        None
    """
    try:
        with open('./device_data.json') as dataFile:
            data = json.load(dataFile)
            for device in data['devices_data']:
                print(device['device_name'], device['ip_address'])
    except FileNotFoundError:
        with open('./device_data.json', 'a') as data_file:
            json.dump(initial_data, data_file, indent=2)


def update_json(data: list) -> None:
    """
    This function updates the json file with the provided data

    :param data:
    :return: None
    """
    new_data: dict = {"devices_data": data}
    with open('./device_data.json', 'w') as data_file:
        json.dump(new_data, data_file, indent=2)


def validate_ip(ip: str) -> None:
    """
    This function validates the ip address entered by the user: checks for if every
    part is less than 256 and total of 4 parts

    :param ip:
    :return:
    """
    ip_list: list = ip.split('.')
    if len(ip_list) != 4:
        raise Exception("Invalid ip")
    for ip_no in ip_list:
        if int(ip_no) > 255:
            raise Exception("Invalid ip")


def get_proper_name(name: str) -> str:
    """
    This function truncates the name and checks if only spaces are entered

    :param name:
    :return: proper_name
    """
    name_list: list = name.split(' ')
    without_space: list = [curr_name for curr_name in name_list if len(curr_name)]
    proper_name: str = ' '.join(without_space)
    return proper_name


def get_required_device(_id: int) -> int | dict:
    """
    This function checks for if a particular device with given id exists in case of edit or adding a device
    :param _id:
    :return:
        -1 (if device not there)
        device dictionary if it's there
    """
    try:
        with open('./device_data.json', 'r') as devices_file:
            devices: Any = json.load(devices_file)
            required_device: list = [device for device in devices['devices_data'] if device['id'] == _id]
    except FileNotFoundError:
        with open('./device_data.json', 'a') as data_file:
            json.dump(initial_data, data_file, indent=2)
    return -1 if len(required_device) == 0 else required_device[0]


def add_device() -> None:
    """
    This function is used for adding the device data in the json

    :return: None
    """
    curr_id = int(input("Enter the id "))
    try:
        with open('./device_data.json', 'r') as dataFile:
            device_data = json.load(dataFile)
            data = device_data['devices_data']
            flag = True
            while flag:
                for i in range(len(data)):
                    if data[i]['id'] == curr_id:
                        flag = False
                        print("This Id already exists")
                        curr_id = int(input("Enter new Id: "))
                        break
                if not flag:
                    flag = True
                elif flag:
                    flag = False
            print("The current id is {}".format(curr_id))
    except FileNotFoundError:
        with open('./device_data.json', 'a') as data_file:
            json.dump(initial_data, data_file, indent=2)
    curr_device_name = input("Enter device name: ")
    flag = True
    while flag:
        name = get_proper_name(curr_device_name)
        if len(name) == 0:
            curr_device_name = input('Enter a valid name: ')
        else:
            curr_device_name = name
            flag = False

    curr_ip = input("Enter ip of device: ")
    validate_ip(curr_ip)
    new_device = {"id": curr_id,
                  "ip_address": curr_ip,
                  "device_name": curr_device_name}
    data.append(new_device)
    update_json(data)


def edit_device(_id: int):
    """
    Edits the data of a particular device with given id

    :param _id:
    :return: None
    """
    required_device = get_required_device(_id)
    if required_device == -1:
        raise Exception("No device found with id {} to edit".format(_id))
    new_name = input("Enter new name: ")
    if new_name == '':
        new_name = required_device['device_name']
    new_ip = input("Enter new ip: ")
    if new_ip == '':
        new_ip = required_device['ip_address']
    edited_device = {
        "id": _id,
        "device_name": new_name,
        "ip_address": new_ip
    }
    try:
        with open('./device_data.json', 'r') as device_file:
            devices = json.load(device_file)
            updated_devices = list(map(lambda device: edited_device if device['id'] == _id else device, devices['devices_data']))
    except FileNotFoundError:
        with open('./device_data.json', 'a') as data_file:
            json.dump(initial_data, data_file, indent=2)
    update_json(updated_devices)


def delete_device(_id):
    """
    Deletes the device from the device_data.json with the provided id

    :param _id:
    :return: None
    """
    try:
        with open('./device_data.json', 'r') as data_file:
            devices = json.load(data_file)
            updated_device = list(filter(lambda device: False if device['id'] == _id else True, devices['devices_data']))
    except FileNotFoundError:
        with open('./device_data.json', 'a') as data_file:
            json.dump(initial_data, data_file, indent=2)
    update_json(updated_device)


def start_ping():
    """
    Function to start pining the device
    :return: None
    """
    while True:
        status = get_status()
        update_csv(status)
        time.sleep(5*60)


if __name__ == '__main__':
    arguments = sys.argv
    if len(arguments) == 1:
        start_ping()
    else:
        if arguments[1] == 'list-devices':
            list_devices()
        elif arguments[1] == 'add-device':
            add_device()
        elif arguments[1] == 'edit-device':
            if len(arguments) == 2:
                raise Exception("Enter valid command")
            edit_device(int(arguments[2]))
        elif arguments[1] == 'delete-device':
            if len(arguments) == 2:
                raise Exception("Enter valid command")
            delete_device(int(arguments[2]))

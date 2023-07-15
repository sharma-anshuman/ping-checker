import time
import json
from typing import Any
from pythonping import ping
from csv import writer
import datetime as dt


def get_device_status() -> list:
    """
    This function returns the status of all the devices present in the
    devicedata.json file by pinging them one by one

    :parameter:
        None
    :return:
        list: a list of status of different devices
    """
    status = []
    with open('./devicedata.json', 'r') as dataFile:
        device_data = json.load(dataFile)
        for device in device_data['devices_data']:
            is_connected = list(ping(device['ip_address'], verbose=False, count=1))
            if str(is_connected[0]) == "Request timed out":
                status.append(0)
            else:
                status.append(1)
    return status


def update_csv_and_json(status: list) -> None:
    """
    This function updates the csv file using status list and devicedata.json
    Also, it adds the current status to the "status" list of devicedata.json

    :param status:
    :return:
        None
    """
    with open('./devicedata.json', 'r+') as dataFile:
        data: Any = json.load(dataFile)
        status_csv: Any = open('./device_pings.csv', 'a')
        add_csv: Any = writer(status_csv)
        for idx, device in enumerate(data['devices_data']):
            device['status'].append(status[idx])
            add_csv.writerow([device["id"], device["device_name"], status[idx], dt.datetime.now().time()])
        dataFile.seek(0)
        json.dump(data, dataFile, indent=2)
        status_csv.close()


def main():
    # Main function to get the statuses and updating the json and csv
    status: list = get_device_status()
    update_csv_and_json(status)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(5*60)  # calling the main after every 2 minutes

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

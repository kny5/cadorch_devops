#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:19:29 2025

@author: kny5
"""

import asyncio
import concurrent.futures
import logging
import time
import functools
import requests  # Using requests for API calls
import traceback
import psutil
from concurrent.futures import ProcessPoolExecutor
import os


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s\t %(levelname)s:\t %(filename)s\t %(funcName)s:\t %(message)s",
    force=True)

logger = logging.getLogger()

def get_system_usage():
    return {
        "cpu_usage": psutil.cpu_percent(interval=None),
        "ram_usage": psutil.virtual_memory().percent,
        "pid": os.getpid()
    }


async def manage_async_pool(status):
    """
    this function creates a async task using concurrent futures.
    """
    with ProcessPoolExecutor() as pool:
        while status:
            logging.info("PID: %s", os.getpid())
            loop = asyncio.get_running_loop()
            usage = await loop.run_in_executor(pool, get_system_usage)
            logger.info(
                "System Status: CPU: %.1f%% | RAM: %.1f%% | PID: %s",
                usage["cpu_usage"], usage["ram_usage"], usage["pid"]
            )
            await asyncio.sleep(5)



# Get the list of devices from the API
SERVER = "http://0.0.0.0:8001"
END_POINT = "get-config-options"
CONFIG_URL = f"{SERVER}/{END_POINT}"
devices_json = requests.get(CONFIG_URL).json()


try:
    devices_list = [
    item['value']
    for option in devices_json['options']
    for add_option in option['add-options']
    for item in add_option['items']]
    

except Exception as e:
    logging.error("Error parsing devices JSON: %s", e)
    devices = []

logging.info("%s extracted devices: %s", len(devices_list), devices_list)

# Shared ThreadPoolExecutor
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        # logging.info("%s, %s",result, elapsed_time)
        return result, elapsed_time
    return wrapper



def function_try_catcher(func):
    """
    Wraps a function to catch and log exceptions, preventing crashes.
    Logs errors using the root logger.
    """
    if asyncio.iscoroutinefunction(func):  # Check if it's an async function
        @functools.wraps(func)
        async def async_wrap(*args, **kwargs):
            try:
                logging.info("Async Executing: %s with args: %s, kwargs: %s",
                             func.__name__, repr(args), repr(kwargs))
                return await func(*args, **kwargs)
            except Exception as e:
                logging.error("Unexpected error in %s: %s\n%s args: %s",
                                 func.__name__, e, traceback.format_exc(), *args)
            # finally:
                return *args, None
        return async_wrap

    @functools.wraps(func)
    def sync_wrap(*args, **kwargs):
        try:
            logging.info("Executing: %s with args: %s, kwargs: %s",
                         func.__name__, repr(args), repr(kwargs))
            return func(*args, **kwargs)

        except Exception as e:
            logging.error("Unexpected error in %s: %s\n%s args: %s",
                             func.__name__, e, traceback.format_exc(), *args)
        # finally:
            return *args, None

    return sync_wrap

@timer
@function_try_catcher
def generate_device(device):
    """
    Calls an API to generate a device and returns the response.
    """
    API_URL = f"{SERVER}/orchestrate"
    payload = {"config": {"device-ids": [device]}}
    headers = {"accept": "application/json"}
    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code == 200:  # Raise error if request fails
        logging.info("Device: %s, Response: %s", device, response.status_code)
        uid = response.json()['unique_name']
        return device, response.status_code, f"{SERVER}/cache/{uid}_assembly_docs/"
        
    else:
        logging.error("Device: %s, Response: %s", device, response.status_code)
        return device, response.status_code, None

async def multiprocess(device):
    """
    Runs generate_device in a separate thread using ThreadPoolExecutor.
    """
    loop = asyncio.get_running_loop()
    # logging.info("Processing device %s in PID: %s", device, os.getpid())

    result = await loop.run_in_executor(executor, generate_device, device)
    return result

import csv

async def main():
    """
    Runs multiprocess on all devices asynchronously.
    """
    tasks = [multiprocess(device) for device in devices_list]
    results = await asyncio.gather(*tasks)
    
    output = [[result[0][0], result[0][1], result[0][2], result[1]] for result in list(results)]
        
    logging.info("All %s devices processed. Results: %s", len(results), results)
    # print("Results:", results)
    
    return to_csv(output)



def to_csv(input):
    with open("test_01.csv", "w") as csv_file:
        write = csv.writer(csv_file)
        write.writerow(["device_name", "status_code","doc_url","process_time", "cpu_percent", "ram_percent"])
        write.writerows(input)
        
# Run both async functions together in the same event loop
async def main_async():
    await asyncio.gather(
        manage_async_pool(),  # Runs system monitoring
        main()                # Runs another async task
    )

# Start the event loop
if __name__ == "__main__":
    asyncio.run(main())

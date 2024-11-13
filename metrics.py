import psutil
import time
import threading
from functools import wraps

## function to get active thread count
def getActiveThreadCount():
    return threading.active_count()

## function to log current resource usage(cpu and memory)
def logResourceUsage():
    cpu_percent = psutil.cpu_percent(interval=1) ## get cpu usage
    memory_info = psutil.virtual_memory() ## get memory usage
    print(f"CPU Usage: {cpu_percent}%")
    print(f"Memory Usage: {memory_info.percent}%")

## function to track execution time()
def trackExecutionTime(func):
    @wraps(func) ## using the wraps from functools
    def wrapper(*arge,**kwargs):
        start_time = time.time() ## start time before function
        result = func(*arge,**kwargs) ## call original function
        end_time = time.time() ## end time after function finished
        execution_time = end_time-start_time
        print(f"{func.__name__} processed in {execution_time:.2f} seconds.") ## print execution time
        return result ## return the funnction result
    return wrapper
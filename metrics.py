import psutil
import time
import threading
import logging
from functools import wraps

## setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

## function to get active thread count
def getActiveThreadCount():
    """
    returns active thread count currently in, used by the program.
    """
    try:
        activeCount = threading.active_count()
        logging.info(f"Current active thread count: {activeCount}".)
        return activeCount
    
    except Exception as e:
        logging.error(f"Error getting active thread count: {e}")
        return 0
    

## function to log current resource usage(cpu and memory)
def logResourceUsage():
    """
    returns the cpu and the memory usage
    """
    try:
        ## get cpu usage
        cpuPercent = psutil.cpu_percent(interval=1) ## get cpu usage
        logging.info(f"CPU Usage: {cpuPercent}%")
        
        ## get memory usage
        memoryInfo = psutil.virtual_memory() ## get memory usage
        logging.info(f"Memory Usage: {memoryInfo.percent}%")
    
    ## error logging
    except Exception as e:
        logging.error(f"Error in logging resorce usage: {e}.")


## function to track execution time()
def trackExecutionTime(func):
    """
    this is a decorator function used to check execution tim eof a function.
    example(how to use):
    @trackExecutionTime ## call fucntion first
    def myFunction():
        my function code
    
    myFunction() ## time will get logged because @trackExecutionTime is added before creating myFunction.
    """
    @wraps(func) ## using the wraps from functools
    def wrapper(*arge,**kwargs):
        start_time = time.time() ## start time before function
        result = func(*arge,**kwargs) ## call original function
        end_time = time.time() ## end time after function finished
        execution_time = end_time-start_time
        ## logging execution time
        logging.info(f"{func.__name__} processed in {execution_time:.2f} seconds.") ## print execution time
        return result ## return the funnction result
    return wrapper
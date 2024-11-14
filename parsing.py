import os
import fitz ## PyMuPDF
import pytesseract 
from pdfminer.high_level import extract_text ## ecract_text from pdfminer
from pymongo import MongoClient ## mongooclient 
from config import mongoUri, databaseName, collectionName, partitionSizes, pdfFolderPath ## importing from config.py
import requests
import json
import re
from io import BytesIO
from summarisation import summariseText
from keywords import extractKeywords
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from metrics import trackExecutionTime, logResourceUsage, getActiveThreadCount
from docUpdation import updateProcessedDocument, storeInitialMetadata
import logging

## mongoClient setup
client = MongoClient(mongoUri) 
db = client[databaseName]
collection = db[collectionName]

## setting up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s) - %(levelname)s - %(message)s')


## function to extract text using OCR for scanned files
def extractTextWithOcr(filePath):
    logging.info(f"Starting OCR extraction for file path: {filePath}.") ## log the start
    text = "" ## variable to add tect
    
    try:
        pdf = fitz.open(filePath) ## opeing with PyMuPDF
        for page in pdf:
            text += pytesseract.image_to_string(page.get_pixmap()) ## using the pytesseract module
        logging.info(f"OCR extraction completed for {filePath}.") ## log the success
    except Exception as e:
        logging.error(f"Error extracting with OCR for {filePath}: {e}.") ## log the failure
    return text


## function to extract text from local pdf file
def extractTextFromPdf(filePath):
    logging.info(f"Starting extraction for file path: {filePath}.") ## log the start
    
    try:
        text = extract_text(filePath) ## extracting text from provided file path
        logging.info(f"Extraction completed for {filePath}.")

        if not text.strip(): ## stripping text
            logging.info(f"No text found, attempting OCR for {filePath}")
            text = extractTextWithOcr(filePath) ## calling the extractTextWithOcr function
        
        return text  ## returning text
    
    except Exception as e:
        logging.error(f"Error extracting text for {filePath}: {e}")
        return ""


## function to download pdf from url and save it locally
def downloadPdfFromUrl(url):
    logging.info(f"Starting to download PDF from URL: {url}")
    
    try: 
        response = requests.get(url) ## reuest from provided url
        response.raise_for_status() ## check for errors

        ## clean the filename from url
        fileName = re.sub(r'[^A-Za-z0-9]','_', url.split("/")[-1]) ## checking and removing unwanted characters which cant be used in filename
        filePath = os.path.join(os.getcwd(), fileName) ## joining current working directory and filename

        with open(filePath, 'wb') as f: ## opeing file path
            f.write(response.content) ## writing content to file path

        logging.info(f"Downloaded pdf: {filePath}") ## log successful download
        return filePath
    
    except Exception as e:
        logging.error(f"Error downloadig pdf from {url}: {e} ") ## log any errors
        return None


## function to extract text from pdf given its url(download pdf)
def extractTextFromUrl(url):
    logging.info(f"Starting to extract text from URL stream: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status() ## check for http errors

        ## open pdf using BytesIO
        pdfData = BytesIO(response.content)

        ## open pdf from BytesIO object
        pdfDocument = fitz.open(stream=pdfData, filetype="pdf")
        
        ## extract text from document
        text = ""
        for pageNum in range(pdfDocument.page_count):
            page = pdfDocument.load_page(pageNum)
            text += page.get_text()
        
        if not text.strip():
            logging.warning(f"No text extracted from URL: {url}") ## log failure

        logging.info(f"Successfully extracted text from URL:{url}") ## log success
        return text

    except Exception as e:
        logging.error(f"Error extracting text from URL {url}:{e}") ## log error
        return ""
    

## function to partition text into categories
def partitionText(text):
    logging.info(f"Starting partitioning text into categories.")
    pages = text.split("\n\n") ## splitting text to new lines

    ## partitioning pasges based on partitionSizes(config.py)
    if len(pages) <= partitionSizes["short"]:
        lengthCategory = "short"
    elif len(pages) <= partitionSizes["medium"]:
        lengthCategory = "medium"
    else:
        lengthCategory = "long"
    logging.info(f"Succesfully partitioned as {lengthCategory} with {len(pages)} pages.") 
    
    return lengthCategory, pages
    
    
## function to process a single pdf file
@trackExecutionTime ## track execution time
def processPdf(filePath):
    logging.info(f"Starting to process PDF from {filePath}.")
    logResourceUsage() ## log resorce usage at start

    ## log active thread count
    activeThreadCountStart = getActiveThreadCount()
    logging.info(f"Active thread count beofre processing {filePath}: {activeThreadCountStart}")

    try:
        size = os.path.getsize(filePath) ## get the file size
        logging.info(f"File size of {filePath}: {size} bytes.")

        storeInitialMetadata(filePath, size) ## store initial metadata in mongodb
        logging.info(f"Stored initial metadata for {filePath} in MongoDB.")

        text = extractTextFromPdf(filePath) ## calling tha above created function
        if text:
            lengthCategory, pages = partitionText(text)
            summary = summariseText(text) ## calling summariseText from summarisation.py
            keywords = extractKeywords(text) ## calling extractKeywords from keywords.py

            ## calculate processing time
            start_time = datetime.datetime.now()

            ## update mongodb with processed information
            updateProcessedDocument(filePath, summary, keywords, (datetime.datetime.now()-start_time))     

            logging.info(f"Processed {filePath} categorised as {lengthCategory}") ## log success
        else:
            logging.warning(f"Failed to process file path") ## log failure
    
    except Exception as e:
        logging.error(f"Error processing PDF from {filePath}.") ## log error
    
    ## log active thread count after processing
    activeThreadCountEnd = getActiveThreadCount()
    logging.info(f"Active thread count after processing {filePath}: {activeThreadCountEnd}") ## log active thread count
    


## function to process a single url file
@trackExecutionTime ## to track time taken by the processUrl function
def processUrl(url, download=False):
    logging.info(f"Starting PDF processing from URL: {url}")
    logResourceUsage() ## log resorce usage at start

    ## log active thread count
    activeThreadCountStart = getActiveThreadCount() ## thread count at start
    logging.info(f"Active thread count before processing {url} : {activeThreadCountStart}")

    text = ""
    pdfPath = None

    try:
        ## startime to process time
        startTime = datetime.datetime.now()
        logging.info(f"Download flag det to {download}.")

        if download:
            pdfPath = downloadPdfFromUrl(url) ## calling above built function to download text from pdf
            if pdfPath:
                logging.info(f"Downloaded PDF from {pdfPath}.")
                text = extractTextFromPdf(fitz.open(pdfPath)) ## opening pdf using PyMuPDF
        else:
            text = extractTextFromUrl(url) ## using above created function to extract text from provided url
    
        if text:
            logging.info(f"Successfully extracted text from URL: {url}") ## log for success

            lengthCategory, pages = partitionText(text) ## calling the partition text function
            logging.info(f"Text categorized as {lengthCategory}")

            ## summarise and extract keywords
            summary = summariseText(text) ## calling the summarise text function 
            keywords = extractKeywords(text) ## calling the extractKeywords function from keyword.py 
        
            ## calculate processing time
            processingTime = (datetime.datetime.now()-startTime).total_seconds()

            ## create document to update into mongodb
            document = {
                "url": url,
                "lengthCategory": lengthCategory,
                "text": text,
                "summary": summary,
                "keywords": keywords,
                "processedAt": str(datetime.datetime.now()),
                "processingTime": processingTime,
            }
            ## update mongo db
            collection.insert_one(document)
            logging.info(f"Successfully processed and saved data from URL:{url}, categorized as {lengthCategory}")
        
        else:
            logging.info(f"failed to process from URL: {url}")
    
    except Exception as e:
        logging.error(f"Error processing URL {url}: {e}")

    ## log active thread after processing
    activeThreadCountEnd = getActiveThreadCount()
    logging.info(f"Active thread count after processing URL {url} : {e} ")


## function to process json files that may contain file path or url
@trackExecutionTime ## time taken to execute the function
def processJson(filePath):
    logging.info(f"Starting PDF processing from JSON: {filePath}")
    logResourceUsage() ## log resorce usage at start

    ## log active thread count at start
    activeThreadCountStart = getActiveThreadCount()
    logging.info(f"Active thread count before processing {json} : {activeThreadCountStart}")

    ## local variableds to store success and failure count
    successCount = 0 ## count varisable for success
    failureCount = 0 ## count variable for failure

    try:
        with open(filePath,'r') as jsonFile:
            data = json.load(jsonFile) ## load json data
            logging.info(f"Succesfully loaded JSON: {json} file")
            
            with ThreadPoolExecutor() as executor:
                futures = []

                for key, item in data.items(): ## iterate over dict key : value pairs
                    logging.info(f"Processing items: {key} -> {item}") 

                    ## determine if item is key or file path
                    if isinstance(item, str) and item.lower().startswith('http'):
                        futures.append(executor.submit(processUrl, item))
                        logging.info(f"Scheduled URL for processing: {item}")

                    elif isinstance(item, str) and os.path.isfile(item):
                        futures.append(executor.submit(processPdf, item))
                        logging.info(f"Scheduled PDF file for processing: {item}")

                    else:
                        logging.warning(f"Invalid entry in json {key} -> {item}")
                        failureCount += 1

                ## collect reults and any exceptions raised
                for future in as_completed(futures):
                    try:
                        future.result()
                        successCount += 1
                        logging.info(f"Item processed successfully.")

                    except Exception as e:
                        logging.error(f"Error processing item :{e}")
                        failureCount += 1
                        
    except FileNotFoundError:
        logging.error(f"Json file not found: {FileNotFoundError}")
    except json.JSONDecodeError as je:
        logging.error(f"Error decoding JSON file: {je}")
    except Exception as e:
        logging.error(f"Unexpected error processing json file {filePath} : {e}")

    ## print final success and failure
    logging.info(f"\nProcessing complete. Successfully processed {successCount} items.")
    logging.info(f"Failed to process {failureCount} items.")

    ## log active thread count after processing
    activeThreadCountEnd = getActiveThreadCount()
    logging.info(f"Active thread count after processing {json}: {activeThreadCountEnd}")


## function to process all pdfs in folder concurrently
@trackExecutionTime
def processPdfsConcurrently(folderPath):
    logging.info(f"Starting to process all PDFs in {folderPath}")
    logResourceUsage() ## logging resource at the start

    ## log active thread count
    activeThreadCountStart = getActiveThreadCount()
    logging.info(f"Active thread count before processing {folderPath}: {activeThreadCountStart}")

    ## list all PDFs in folder
    pdfFiles = [os.path.join(folderPath, file) for file in os.listdir(folderPath) if file.lower().endswith(".pdf")]

    if not pdfFiles:
        logging.error(f"No PDFs found in {folderPath}")
        return
    
    logging.info(f"Found {len(pdfFiles)} to process.")

    ## use threapooler for concurrent processing
    with ThreadPoolExecutor() as executor:
        futures = {}

        ## submit each pdf file for processing and track futures with file paths
        for filePath in pdfFiles:
            filePath = futures[executor.submit(processPdf, filePath)]
            logging.info(f"Scheduled processing for {filePath}")

        ## wait for futures to complete and check for errors
        for future in futures:
            filePath = futures[future]
            try:
                future.result()
                logging.info(f"Successfully processed {filePath}")
            
            except Exception as e:
                logging.error(f"Error processing: {filePath}")
    
    ## active thread count after processing
    activeThreadCountEnd = getActiveThreadCount()
    logging.info(f"Active thread count after processing PDFs in {folderPath}: {activeThreadCountEnd}")

    logging.info(f"Successfully processed all PDFs in {folderPath}")
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
from metrics import trackExecutionTime, logResourceUsage
from docUpdation import updateProcessedDocument, storeInitialMetadata

## mongoClient setup
client = MongoClient(mongoUri) 
db = client[databaseName]
collection = db[collectionName]


## function to extract text using OCR for scanned files
def extractTextWithOcr(filePath):
    text = "" ## variable to add tect
    pdf = fitz.open(filePath) ## opeing with PyMuPDF
    for page in pdf:
        text += pytesseract.image_to_string(page.get_pixmap()) ## using the pytesseract module
    return text


## function to extract text from local pdf file
def extractTextFromPdf(filePath):
    try:
        text = extract_text(filePath) ## extracting text from provided file path
        if not text.strip(): ## stripping text
            text = extractTextWithOcr(filePath) ## calling the extractTextWithOcr function
        return text  ## returning text
    except Exception as e:
        print(f"error extracting text {e}")
        return ""


## function to download pdf from url and save it locally
def downloadPdfFromUrl(url):
    try:
        response = requests.get(url) ## reuest from provided url
        response.raise_for_status() ## check for errors
        fileName = re.sub(r'[^A-Za-z0-9]','_', url.split("/")[-1]) ## checking and removing unwanted characters which cant be used in filename
        filePath = os.path.join(os.getcwd(), fileName) ## joining current working directory and filename
        with open(filePath, 'wb') as f: ## opeing file path
            f.write(response.content) ## writing content to file path
        print(f"Downloaded pdf: {filePath}")
        return filePath
    except Exception as e:
        print(f"Error downloadig pdf from {url}: {e} ")
        return None


## function to extract text from pdf given its url(download pdf)
def extractTextFromUrl(url):
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
        return text
    except Exception as e:
        print(f"Error extracting text from URL {url}:{e}")
        return ""
    

## function to partition text into categories
def partitionText(text):
    pages = text.split("\n\n") ## splitting text to new lines
    ## partitioning pasges based on partitionSizes(config.py)
    if len(pages) <= partitionSizes["short"]:
        return "short", pages
    elif len(pages) <= partitionSizes["medium"]:
        return "medium", pages
    else:
        return "long", pages


## function to process a single pdf file
@trackExecutionTime ## track execution time
def processPdf(filePath):
    logResourceUsage() ## log resorce usage at start

    size = os.path.getsize(filePath) ## get the file size
    storeInitialMetadata(filePath, size) ## store initial metadata in mongodb

    text = extractTextFromPdf(filePath) ## calling tha above created function
    if text:
        lengthCategory, pages = partitionText(text)
        summary = summariseText(text) ## calling summariseText from summarisation.py
        keywords = extractKeywords(text) ## calling extractKeywords from keywords.py

        ## calculate processing time
        start_time = datetime.datetime.now()

        ## update mongodb with processed information
        updateProcessedDocument(filePath, summary, keywords, (datetime.datetime.now()-start_time))     

        print(f"Processed {filePath} categorised as {lengthCategory}")   
    else:
        print(f"Failed to process file path")


## function to process a single url file
@trackExecutionTime ## to track time taken by the processUrl function
def processUrl(url, download=False):
    logResourceUsage() ## log resorce usage at start

    text = ""
    pdfPath = None

    try:
        ## startime to process time
        startTime = datetime.datetime.now()
        if download:
            pdfPath = downloadPdfFromUrl(url) ## calling above built function to download text from pdf
            if pdfPath:
                text = extractTextFromPdf(fitz.open(pdfPath)) ## opening pdf using PyMuPDF
        else:
            text = extractTextFromUrl(url) ## using above created function to extract text from provided url
    
        if text:
            lengthCategory, pages = partitionText(text) ## calling the partition text function
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
              
            print(f"Processed {url}, categorized as {lengthCategory}")
        
        else:
            print(f"failed to process {url}")
    
    except Exception as e:
        print(f"Error processing URL {url}: {e}")


## function to process json files that may contain file path or url
@trackExecutionTime ## time taken to execute the function
def processJson(filePath):
    logResourceUsage() ## log resorce usage at start

    ## local variableds to store success and failure count
    successCount = 0 ## count varisable for success
    failureCount = 0 ## count variable for failure

    try:
        with open(filePath,'r') as jsonFile:
            data = json.load(jsonFile) ## load json data
            
            with ThreadPoolExecutor() as executor:
                futures = []
                for key, item in data.items(): ## iterate over dict key : value pairs
                    print(f"Processing item : {key}:{item}") ## debug print
                    if isinstance(item, str) and item.lower().startswith('http'):
                        futures.append(executor.submit(processUrl, item))
                    elif isinstance(item, str) and os.path.isfile(item):
                        futures.append(executor.submit(processPdf, item))
                    else:
                        print(f"Invalid entry in json {key}:{item}")
                        failureCount += 1

                ## collect reults(exceptions raised)
                for future in as_completed(futures):
                    try:
                        future.result()
                        successCount += 1
                    except Exception as e:
                        print(f"Error processing item :{e}")
                        failureCount += 1
                        
    except Exception as e:
        print(f"error processing json file {filePath} : {e}")

    ## print final success and failure
    print(f"\nProcessing complete. Successfully processed {successCount} items.")
    print(f"Failed to process {failureCount} items.")


## function to process all pdfs in folder concurrently
@trackExecutionTime
def processPdfsConcurrently(folderPath):
    logResourceUsage() #3 logging resource at the start
    ## list all files in folder
    pdfFiles = [os.path.join(folderPath, file) for file in os.listdir(folderPath) if file.lower().endswith(".pdf")]

    ## use threapooler for concurrent processing
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(processPdf, filePath) for filePath in pdfFiles]

        ## wait for futures to complete and check for errors
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error processing file: {e}")
from pymongo import collection
import datetime
from pymongo import errors

## update document
def update_document(filePath, summary, keywords):
    collection.update_one(
     {"file_path": filePath}, ## filter to find document
      {"$set": {"summary": summary, "keywords": keywords}}  ## update document
    )


## function to store initial metadata in mongodb
def storeInitialMetadata(filePath, size):
    ## creating a metadata dictionary 
    try:
        metadata = {
            "filePath" : filePath,
            "size" : size,
            "ingestedAt" : datetime.datetime.now() ## store as datetime object
        }
        
        ## insert data into mongodb
        result = collection.InsertOne(metadata)

        ## print confirmation message
        print(f"Initial metadata dtored for {filePath}. Document ID: {result.inserted_id}")
    
    except errors.PyMongoError as e:
        print(f"Failed to store metadata for {filePath} due to error {e}")
        


## function to update mongodb entry with summary and keywords after processing
def updateProcessedDocument(filePath,summary, keywords,processingTime):
    ## converting time to seconds
    try:
        processingTimeInSeconds = processingTime.total_seconds()

        ## creating a dictionary for updating data
        updateData = {
            "summary" :  summary, ## summary
            "keywords" : keywords, ## keywords
            "processingTime" : processingTimeInSeconds, ## storing as seconds
            "processedAt" : datetime.datetime.now() ## datetime object 
        }

        ## ingesting data into mongodb
        result = collection.UpdateOne(
            {"filePath" : filePath}, ## matching file path
            {"$set" : updateData} ## updating the summary keywords and processing time
        )

        ## check if document is matched and modified
        if result.matched_count > 0:
            print(f"Document updated for {filePath}")
        else:
            print(f"No document found for {filePath}. No update performed.")
    
    ## checking pymongo error
    except errors.PyMongoError as e:
        print(f"Failed to update document for filePath: {filePath}. Error: [e]")
    
    ## checking any other error
    except Exception as e:
        print(f"An unexpected error has occured: {e}.")
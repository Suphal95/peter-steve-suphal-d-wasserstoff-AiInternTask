from pymongo import collection
import datetime

## update document
def update_document(file_path, summary, keywords):
    collection.update_one(
     {"file_path": file_path,
      "$set": {"summary": summary, "keywords": keywords}}   
    )


## function to store initial metadata in mongodb
def storeInitialMetadata(filePath, size):
    ## creating a metadata dictionary 
    metadata = {
        "filePath": filePath,
        "size": size,
        "ingestedAt": str(datetime.datetime.now())
    }
    collection.insert_one(metadata) ## insert metadata into mongodb
    print(f"Initial metadata stored for {filePath}.")


## function to update mongodb entry with summary and keywords after processing
def updateProcessedDocument(filePath,summary, keywords,processingTime):
    ## converting time data to total seconds
    processingTimeInSeconds = processingTime.total_seconds()
    ## create a dictionary for update data
    updateData = {
        "summary": summary,
        "keywords": keywords,
        "processingTime": processingTimeInSeconds, ## storing as seconds
        "processedAt": str(datetime.datetime.now())
    }
    ## ingesting data into mongodb
    collection.update_one(
        {"filePath": filePath}, ## matching filepath
        {"$set": updateData} ## updating summary, keywords and processing time
        )
    print(f"Document updated for {filePath}")
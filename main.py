import os
from parsing import processPdf, processUrl, processJson, processPdfsConcurrently
from config import pdfFolderPath
import logging
import time

def main():
    logging.info(f"Pdf Processing Pipeline Started.")
    print("PDF Processing Pipeline")
    print("=======================")
    print("Choose an option")
    print("1. Process all PDFs in a folder (concurrently)")
    print("2. Process a single pdf file")
    print("3. Process a PDF from URL")
    print("4. Process a Json file")
    print("5. Exit")
    
    while True:
        choice = input("Enter your choice(1-5): ")
    
        if choice == '1':
            ## option 1 process all pdfs in the folder
            folderPath = input(f"Enter the folder path (Default: pdfFolderPath): ") or pdfFolderPath
            logging.info(f"User selected to processing all pdfs in folder: {folderPath}.")

            if os.path.isdir(folderPath):
                processPdfsConcurrently(folderPath)
                logging.info("Completed processing all PDFs in folder")
                print(f"Processing all PDFs in folder completed.")
            else:
                logging.error(f"Invalid folder path: {folderPath}")
                print(f"Invalid folder path: {folderPath}")
    
        elif choice == '2':
            ## Option 2: Process a single PDF file
            filePath = input("Enter the path to PDF file: ")
            logging.info(f"User selected to process single PDF file: {filePath}")
            
            if os.path.isfile(filePath) and filePath.lower().endswith(".pdf"):
                processPdf(filePath)
                logging.info(f"Completed processing single PDF: {filePath}")
                print(f"\nProcessing single PDF completed.")
            else:
                logging.error(f"Invalid PDF file path: {filePath}")
                print(f"Invalid file path: {filePath}")

        elif choice == '3':
            ## Option 3: Process PDF from URL
            url = input("Enter the PDF URL: ")
            logging.info(f"User selected to process PDF from URL: {url}")
            
            if url.lower().startswith("http"):
                processUrl(url)
                logging.info(f"Completed processing PDF from URL: {url}")
                print(f"Processing PDF from URL completed.")
            else:
                logging.error(f"Invalid URL: {url}")
                print(f"Invalid URL: {url}")

        elif choice == '4':
            ## option 4 process a json file
            jsonFilePath = input("Enter the path to the JSON file: ")
            logging.info(f"User selected to process JSON file: {jsonFilePath}")
            
            if os.path.isfile(jsonFilePath) and jsonFilePath.lower().endswith(".json"):
                processJson(jsonFilePath)
                logging.info(f"Completed processing JSON file: {jsonFilePath}")
                print(f"Processing JSON file completed.")
            else:
                logging.error(f"Invalid JSON file path: {jsonFilePath}")
                print(f"Invalid JSON file: {jsonFilePath}")
    
        elif choice == '5':
            logging.info("User chose to exit the pipeline")
            print("Exiting the pipeline")
            break
        
        else:
            logging.warning(f"User entered an invalid choice: {choice}")
            print("Invalid choice! Please enter a valid choice (1-5).")
    
        ## prompt to restart or exit
        restart = input("\nDo you want to process another set of files (y/n)? ").lower()
        if restart != 'y':
            logging.info("User chose to exit after processing")
            print("Pipeline execution completed!")
            break

    logging.info(f"PDF Processing Pipeline Ended.")

    
    
if __name__ == "__main__":
    main()

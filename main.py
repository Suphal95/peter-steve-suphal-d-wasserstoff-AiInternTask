import os
from parsing import processPdf, processUrl, processJson, processPdfsConcurrently
from config import pdfFolderPath
import time

def main():
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
            processPdfsConcurrently(folderPath)
            print(f"Processing all pdfs in folder completed.")
    
        elif choice == '2':
            ## option 2 process a single pdf file
            filePath = input("Enter the path to PDF file: ")
            
            if os.path.isfile(filePath) and filePath.lower().endswith(".pdf"):
                processPdf(filePath)
                print(f"\nProcessing single PDF completed.")
            else:
                print(f"Invalid file path: {filePath}")

        elif choice == '3':
            ## option 3 process pdf from url
            url = input("Enter the PDF URL: ")
            if url.lower().startswith("http"):
                processUrl(url)
                print(f"Processing PDF from URL completed.")
            else:
                print(f"Invalid URL: {url}")

        elif choice == '4':
            ## option 4 process a json file with pdf link or path
            jsonFilePath = input(f"Enter the path to the Json file: ")
            if os.path.isfile(jsonFilePath) and jsonFilePath.lower().endswith(".json"):
             processJson(jsonFilePath)
             print(f"Processing JSON file completed.")
            else:
                print(f"Invalid Json file: {jsonFilePath}")
    
        elif choice == '5':
            print(f"Exiting the pipeline")
    
        else:
            print("invalid choice! Please enter a valid choice(1-5).")
    
        ## prompt to restart or exit
        restart = input("\n Do you want to process another set of files(y/n)? ").lower()
        
        if restart != 'y':
            print("Pipeline execution Complted!")
            break

    
if __name__ == "__main__":
    main()

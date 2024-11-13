PDF Processing Pipeline

1.0 Overview
    - This project is a PDF Processing Pipeline designed to handle multiple PDF documents concurrently. 
    - It supports extracting text from PDF files (local and from URLs), generating summaries, extracting keywords, and storing the processed data in a MongoDB database. 
    - The pipeline is efficient, scalable, and capable of handling documents of various lengths, including scanned PDFs using OCR.

2.0 Features
    - Concurrent PDF Processing: Process multiple PDFs simultaneously for faster execution.
    - Text Extraction: Extract text using both pdfminer and PyMuPDF, with OCR support for scanned documents using pytesseract.
    - Summarization: Generate summaries using a transformer model (distilbart-cnn-12-6).
    - Keyword Extraction: Extract keywords using TF-IDF Vectorization.
    - MongoDB Integration: Store document metadata, summaries, and keywords in MongoDB.
    - Metrics Logging: Track CPU, memory usage, and execution time for performance analysis.

3.0 Table of Contents
    - Setup Instructions
    - Configuration
    - Usage
    - Functionality Breakdown
    - MongoDB Schema
    - Future Improvements

3.1 Setup Instructions
    3.1.1 Prerequisites :
        - Make sure you have the following installed:
        - Python 3.12.7
        - MongoDB (running locally or a configured URI) 
        - Required Python packages (listed in requirements.txt)

    3.1.2 Installation:
          - Clone the Repository.
          - git clone https://github.com/Suphal95/peter-steve-suphal-d-wasserstoff-AiInternTask.git
          - cd peter-steve-suphal-d-wasserstoff-AiInternTask

    3.1.3 Create a Virtual Environment
          - python -m venv venv
          - venv\Scripts\activate - windows 
          - source venv/bin/activate - mac
    
    3.1.4 Install Dependencies
          pip install -r requirements.txt
    
    3.1.5 MongoDB Setup
          - Ensure MongoDB is running locally on mongodb://localhost:27017/ or update the URI in the config.py file.

    3.1.6 Additional Setup for OCR (Optional)
          - Tesseract OCR:
            Install Tesseract
          - Add Tesseract to your system's PATH.
          - For Windows, you may need to specify the Tesseract executable path:
          - pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" ## for referance

3.2 Configuration
    - The project configuration is managed through config.py:
      mongoUri: MongoDB connection string.
      databaseName: Name of the MongoDB database.
      collectionName: Name of the collection to store documents.
      pdfFolderPath: Default folder path for bulk PDF processing.
      partitionSizes: Criteria for categorizing document length.

3.3 Usage
    - Run the pipeline using the main entry point:
      python main.py ## in terminal
      Options:
      1: Process all PDFs in a folder (concurrently).
      2: Process a single PDF file.
      3: Process a PDF from a URL.
      4: Process a JSON file with links to PDFs.
      5: Exit the program.

    - For option 4, the JSON file should have the following structure:
      {
      "document1": "http://example.com/file1.pdf",
      "document2": "C:/Users/Steve/Desktop/file2.pdf"
       }

3.4 Functionality Breakdown
    3.4.1 Parsing PDFs (parsing.py)
          - Extracts text from local PDFs and URLs.
          - Supports OCR for scanned PDFs.
          - Categorizes documents based on their length.
          - Stores metadata in MongoDB.
    3.4.2 Summarization (summarisation.py)
          - Uses the distilbart-cnn-12-6 model to generate summaries.
          - Adjusts summary length based on document size.
    3.4.3 Keyword Extraction (keywords.py)
          - Uses TF-IDF to extract top N keywords from the text.
    3.4.4 Performance Metrics (metrics.py)
          - Logs CPU and memory usage.
          - Tracks execution time for each processing function.
    3.4.5 Database Updation (docUpdation.py)
          - Updates MongoDB entries with summaries and keywords after processing.

3.5 MongoDB Schema
      - The MongoDB collection uses the following schema:
        Fields:
        filePath/url: Source of the PDF.
        size: File size in bytes.
        ingestedAt: Timestamp of when the file was ingested.
        text: Full extracted text.
        summary: Generated summary of the document.
        keywords: Extracted keywords.
        processingTime: Time taken to process the document (in seconds).
        processedAt: Timestamp of processing completion.
        lengthCategory: Categorization of document size (short, medium, long).

3.6 Future Improvements
      Additional NLP Models: Experiment with other summarization models for better accuracy.
      Scalability: Implement asynchronous processing with asyncio.
      Error Handling: Improve error handling and logging for better debugging.
      Web Interface: Develop a Flask/Django-based UI for easier interaction.

4.0 License
      This project is licensed under the MIT License.
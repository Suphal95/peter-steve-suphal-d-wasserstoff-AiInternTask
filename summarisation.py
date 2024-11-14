from transformers import pipeline

summariser = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", tokenizer="sshleifer/distilbart-cnn-12-6")

def summariseText(text, maxInputLength=1024):
    ## check if input text is valid(not empty)
    if not isinstance(text, str) or not text.strip():
        print("The input text is error or invalid.")
        return ""
    
    ## check max input length
    if not isinstance(maxInputLength, int) or maxInputLength <= 0:
        print("Error. Max input length must be a positive integer.")
        return ""

    ## tokenize the input to check its length
    inputTokens = summariser.tokenizer(text, truncation=True, padding='longest', max_length=maxInputLength, return_tensors="pt")
    
    ## check number of tokens
    documentLength = inputTokens.input_ids.shape[1] ## number of tokens in input

    ## truncate input tokens if they exceed models max input length
    if documentLength > maxInputLength:
        inputTokens = inputTokens.input_ids[0][:maxInputLength]
        text = summariser.tokenizer.decode(inputTokens, skip_special_tokens=True)
        print(f"input text truncated to {maxInputLength} tokens")

    ## adjust summary length for short, medium, long and very long documents
    if documentLength <= 100: ## short document
        maxSummaryLength = 50 
        minSummaryLength = 20 
    elif documentLength <= 500: ## medium document
        maxSummaryLength = 100 
        minSummaryLength = 30 
    elif documentLength <= 1000: ## long document
        maxSummaryLength = 150
        minSummaryLength = 50 
    else:
        maxSummaryLength = 300 ## long summary
        minSummaryLength = 100
    
    print(f"Document length: {documentLength}, maxSummaryLength: {maxSummaryLength}, minSummaryLength: {minSummaryLength}")

    try:
        ## generate summary
        summary = summariser(text,
                              max_new_tokens=maxSummaryLength,
                              min_length=minSummaryLength,
                              truncation=True,
                              do_sample=False) ## adjust min length as needed for more control

        print(f"Generated summary: {summary}")
        
        ## return summary text
        if summary and len(summary) > 0:
            return summary[0]['summary_text']
        else:
            return ""
    
    ## errors checking
    except ValueError as ve:
        print(f"Value error during summarisation: {ve}")
        return ""
    
    except KeyError as ke:
        print(f"Value error during summarisation: {ke}")
        return ""
    
    except Exception as e:
        print(f"Error during summarisation: {e}")
        return ""
from transformers import pipeline

summariser = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", tokenizer="sshleifer/distilbart-cnn-12-6")

def summariseText(text, max_input_length=1024):
    ## tokenize the input to check its length
    input_tokens = summariser.tokenizer(text, truncation=True, padding='longest', max_length=max_input_length, return_tensors="pt")
    
    ## check number of tokens
    document_length = input_tokens.input_ids.shape[1] ## number of tokens in input

    ## truncate input tokens if they exceed models max input length
    if document_length > max_input_length:
        input_tokens = input_tokens.input_ids[0][:max_input_length]
        text = summariser.tokenizer.decode(input_tokens, skip_special_tokens=True)
        print(f"input text truncated to {max_input_length} tokens")

    ## adjust summary length for short, medium, long and very long documents
    if document_length <= 100: ## short document
        max_summary_length = 50 
        min_summary_length = 20 
    elif document_length <= 500: ## medium document
        max_summary_length = 100 
        min_summary_length = 30 
    elif document_length <= 1000: ## long document
        max_summary_length = 150
        min_summary_length = 50 
    else:
        max_summary_length = 300 ## long summary
        min_summary_length = 100
    
    print(f"Document length: {document_length}, max_summary_length: {max_summary_length}, min_summary_length: {min_summary_length}")

    try:
        ## generate summary
        summary = summariser(text,
                              max_new_tokens=max_summary_length,
                              min_length=min_summary_length,
                              truncation=True,
                              do_sample=False) ## adjust min length as needed for more control

        print(f"Generated summary: {summary}")
        
        ## return summary text
        if summary and len(summary) > 0:
            return summary[0]['summary_text']
        else:
            return ""
        
    except Exception as e:
        print(f"Error during summarisation: {e}")
        return ""
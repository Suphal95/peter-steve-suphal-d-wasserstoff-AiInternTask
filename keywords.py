from sklearn.feature_extraction.text import TfidfVectorizer

def extractKeywords(text, top_n=10, stop_words="english"):
    ## check if input text is valid
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")
    
    if not text.strip():
        print("Warning: Input text is empty or contains only whitespace.")
        return []
    
    ## check top_n is positive integer
    if not isinstance(top_n, int) or top_n <= 0:
        raise ValueError("top_n must be a positive integer.")
    
    try:
        ## initialise tfid vector with stop words and ngram range
        vectorizer = TfidfVectorizer(stop_words=stop_words, ngram_range=(1,2))

        ## create tfid matrix
        TfidMatrix = vectorizer.fit_transform([text])

        ## create list of tuples for (term,score) and sort by score
        scores = zip(vectorizer.get_feature_names_out(), TfidMatrix.toarray()[0])
        sortedScores = sorted(scores, key=lambda x:x[1], reverse= True)

        ## return top_n keywords
        return [word for word, score in sortedScores[:top_n]]
    
    except Exception as e:
        print(f"An error occured while extracting keywords: {e}.")
        return []


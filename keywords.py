from sklearn.feature_extraction.text import TfidfVectorizer

def extractKeywords(text, top_n=10, stop_words="english"):
    if not text.strip():
        return []
    ## initialize the vector
    vectorizer = TfidfVectorizer(stop_words=stop_words, ngram_range=(1,2)) 
    tfidfMatrix = vectorizer.fit_transform([text])

    scores = zip(vectorizer.get_feature_names_out(), tfidfMatrix.toarray()[0])
    sortedScores =sorted(scores, key=lambda x:x[1], reverse=True)
    return [word for word, score in sortedScores[:top_n]]
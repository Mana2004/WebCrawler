from hazm import Normalizer, WordTokenizer, Stemmer


class PersianPrep:
    def __init__(self):
        self.normalizer = Normalizer()
        self.tokenizer = WordTokenizer()
        self.stemmer = Stemmer()

        self.stopwords = {"و", "در", "به", "از", "که", "این", "را", "با", "است", "ان"}

    def clean_text(self, text):
        if not text:
            return ""

        normalized_text = self.normalizer.normalize(text)

        words = self.tokenizer.tokenize(normalized_text)

        cleaned_words = []
        for word in words:
            stemmed = self.stemmer.stem(word)
            if stemmed not in self.stopwords:
                cleaned_words.append(stemmed)

        return " ".join(cleaned_words)
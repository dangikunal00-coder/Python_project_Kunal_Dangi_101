import os
import requests
import json
from datetime import datetime

class NewsAPIError(Exception):
    #Raised when there is an issue with API communication
    pass

class NoArticlesFound(Exception):
    #Raised when no articles are returned from API
    pass

class Article:
    def __init__(self, title, description, url):
        self.title = title
        self.description = description
        self.url = url

    def __str__(self):
        return f"Title: {self.title}\nDescription: {self.description}\nURL: {self.url}\n"

class NewsReader:
    base_URL = "https://gnews.io/api/v4/search"

    def __init__(self, api_key, language="en", keyword="example"):
        self.api_key = api_key
        self.language = language
        self.keyword = keyword

    def fetch_news(self, max_results=5):
        params = {
            "q": self.keyword,
            "lang": self.language,
            "country": "in",
            "max": max_results,
            "apikey": self.api_key
        }

        try:
            response = requests.get(self.base_URL, params=params)

            if response.status_code != 200:
                raise NewsAPIError(f"API request failed: {response.text}")

            data = response.json()
            articles_data = data.get("articles", [])
            
            if not articles_data:
                raise NoArticlesFound("No news found for this keyword.")

            return [Article(a["title"], a["description"], a["url"]) for a in articles_data]

        except requests.exceptions.RequestException as e:
            raise NewsAPIError(f"Network Error: {e}") from e


    def save_to_file(self, articles, file_format="txt"):
        
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads_path, exist_ok=True)

        filename = f"news_{self.keyword}.{file_format}"
        file_path = os.path.join(downloads_path, filename)

        try:
            if file_format == "txt":
                with open(file_path, "w") as f:
                    for art in articles:
                        f.write(str(art) + "-" * 60 + "\n")

            elif file_format == "json":
                with open(file_path, "w") as f:
                    json.dump([art.__dict__ for art in articles], f)

            return file_path

        except Exception as e:
            raise IOError(f"Error writing file: {e}")


#  Main Program
def main():
    print("     Daily News Reader     ")

    api_key = "ede4239914f8b92522e947702ad94105"

    choice = (input("Press 1 for Hindi news or Press 2 for English news:- "))
    
    lang = "hi" if choice == "1" else "en"
        

    keyword = input("Enter a topic: ")

    reader = NewsReader(api_key, language=lang, keyword=keyword)

    try:
        print(f"\nFetching latest news about '{keyword}'...\n")
        articles = reader.fetch_news()

        print(f"Found {len(articles)} articles.")
        format_choice = input("Save as 1) TXT 2) JSON (default TXT): ")
        file_format = "json" if format_choice == "2" else "txt"

        file_path = reader.save_to_file(articles, file_format)

        print(f"\nDone! File saved at:\n{file_path}")

    except NewsAPIError as e:
        print(f"API Error: {e}")

    except NoArticlesFound as e:
        print(f"{e}")

    except Exception as e:
        print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()
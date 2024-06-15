import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")


def save_report_to_mongodb(title, summary, url, date): 
    db = client["news"]
    news_collection = db["news"]
    
    news_collection.insert_one({
        "title": title,
        "summary": summary,
        "url": url,
        "date": date
    })

def check_if_exists_in_mongodb(url):
    db = client["news"]
    news_collection = db["news"]
    documents = list(news_collection.find({'url': url}))

    return len(documents) > 0
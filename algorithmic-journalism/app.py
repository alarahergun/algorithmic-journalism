import services.fetch_service as fetch_service
import services.open_ai as open_ai
import services.mongo_db as mongo_db
from datetime import date, datetime
import schedule

def fetch_and_process_articles():
  news_articles = []

  news_articles.extend(fetch_service.fetch_cnbc_data())
  news_articles.extend(fetch_service.fetch_guardian_data())
  news_articles.extend(fetch_service.fetch_time_news())

  for article in news_articles:
    if not mongo_db.check_if_exists_in_mongodb(article["url"]):
      summary = open_ai.get_summary_from_model((article["content"]))
      mongo_db.save_report_to_mongodb(article["title"], summary, article["url"], datetime.combine(date.today(), datetime.min.time()))

if __name__ == "__main__":
  # schedule.every().day.at("15:20").do(fetch_and_process_articles)
  fetch_and_process_articles()
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

HTML_PARSER = "html.parser"
headers = { 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" }

def fetch_cnbc_data():
    url = "https://www.cnbc.com/climate/"
    response = requests.get(url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, HTML_PARSER)
    headline_news = soup.find_all("a", attrs={'class': 'Card-title', 'href': True})
    articles = []

    for headline in headline_news:
        # getting article content
        article_url = headline['href']
        article_response = requests.get(article_url)
        article_html_content = article_response.text
        article_soup = BeautifulSoup(article_html_content, HTML_PARSER)
        article_content = ''
        paragraphs = article_soup.find_all(attrs={'class': 'group'})

        for paragraph in paragraphs:
            article_content += paragraph.text

        articles.append({
                "title": headline.text,
                "content": article_content,
                "url": article_url})
        
    return articles

def fetch_guardian_data():
    url = "https://www.theguardian.com/uk/environment"
    response = requests.get(url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, HTML_PARSER)
    container_environment = soup.find("div", attrs={'id': 'container-environment'})
    headline_news = container_environment.find_all("a", attrs={'href': True})
    articles = []

    for headline in headline_news:
        if 'aria-label' in headline.attrs:
            # getting article content
            article_url = headline['href']
            article_response = requests.get("https://www.theguardian.com/" + article_url)
            article_html_content = article_response.text
            article_soup = BeautifulSoup(article_html_content, HTML_PARSER)
            article_content = ''
            paragraphs = article_soup.find_all('p')

            for paragraph in paragraphs:
                article_content += paragraph.text

            articles.append({
                    "title": headline['aria-label'],
                    "content": article_content,
                    "url": "https://www.theguardian.com" + article_url})
            
    return articles

def fetch_time_news():
    BASE_URL = "https://time.com/"

    response = requests.get(BASE_URL + "section/climate/", headers=headers)   
    html_content = response.text
    soup = BeautifulSoup(html_content, HTML_PARSER)
    main_section = soup.find("section", attrs={'class': 'section-curated'})
    more_section = soup.find("section", attrs={'class': 'section-related'})
    headline_news = main_section.find_all("a", attrs={'href': True})
    more_news = more_section.find_all("a", attrs={'href': True})
    headline_news.extend(more_news)
    articles = []

    for article in headline_news:
        try:
            article_url = article['href']
            article_response = requests.get(BASE_URL + article_url)
            article_html_content = article_response.text
            article_soup = BeautifulSoup(article_html_content, HTML_PARSER)
            article_content = ''
            main_div = article_soup.find("div", attrs={'id': 'article-content'})
            main_article_div = main_div.find('article', attrs={'id': 'article-body'})
            paragraphs = main_article_div.find_all('p')

            for paragraph in paragraphs:
                article_content += paragraph.text

            article_header_div = article_soup.find('div', attrs={'id': 'article-header'})

            articles.append({
                "title": article_header_div.find('h1').text,
                "content": article_content,
                "url": BASE_URL + article_url
            })
        except:
            print("Skipping article with href: " + article['href'])

    return articles
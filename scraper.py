import re
import requests
from bs4 import BeautifulSoup
import time
import logging
import sys

import os
from dotenv import load_dotenv
from datetime import datetime
now = datetime.now()

load_dotenv()
topic_name = os.environ["TOPIC_NAME"]

def notify(message, title):
    requests.post(
        f"https://ntfy.sh/{topic_name}",
        data=message.encode("utf-8"),
        headers={"Title": title, "Priority": "high"},
        timeout=10,
    )

def scrape(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    ul = soup.find("ul", class_ = "ul__5IxUHb withMetadata__klorrw")
    if ul is None:
        raise ValueError("Issue list not found (page layout may have changed)")

    li = ul.find("li").get_text(strip=True)
    id = re.search(r"#[0-9]{6}", li)
    
    return [li,id]

def check_change(scraped):
    with open("issue.txt", "r") as f:
        issue = f.read().splitlines()

    li = scraped[0]
    id = scraped[1]
        
    now = datetime.now()
    print(now.strftime("%H:%M") + " : " + '\'' + issue[0] + '\' ' + issue[1])
    
    if issue[1] != id.group():
        print("î Issue changed.")
        notify(f"The first issue has changed to {id.group()}", title="New Issue!")

        with open("issue.txt", "w") as f:
            f.write(li + "\n")
            f.write(id.group() + "\n")

        with open("history.txt", "a") as f:
            f.write(li + "\n")
            f.write(id.group() + "\n")
            f.write("******\n")

def run(url):
    while True:
        try:
            check_change(scrape(url))
        except Exception as e:
            logging.exception("Fatal error, shuttinng down")
            raise
        time.sleep(1800)

url = "https://github.com/llvm/llvm-project/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22"

if __name__ == "__main__":
    try:
        run(url)
    except Exception as e:
        print("Bot stopped.")
        notify(f"The Bot crashed", "Crash!")
        sys.exit(1)


import re
import requests
from bs4 import BeautifulSoup

import os
from dotenv import load_dotenv

load_dotenv()
topic_name = os.environ["TOPIC_NAME"]

def notify(message, title="New Issue!"):
    requests.post(
        f"https://ntfy.sh/{topic_name}",
        data=message.encode("utf-8"),
        headers={"Title": title, "Priority": "high"},
        timeout=10,
    )

url = "https://github.com/llvm/llvm-project/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22"

response = requests.get(url, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

ul = soup.find("ul", class_ = "ListView-module__ul__uMK30")

li = ul.find("li").get_text(strip=True)

id = re.search(r"#[0-9]{6}", li)

with open("issue.txt", "r") as f:
    issue = f.read().splitlines()
    
if issue[1] != id.group():
    notify(f"The first issue has changed to {id.group()}")

    with open("issue.txt", "w") as f:
        f.write(li + "\n")
        f.write(id.group() + "\n")

    with open("history.txt", "a") as f:
        f.write(li + "\n")
        f.write(id.group() + "\n")
        f.write("******\n")
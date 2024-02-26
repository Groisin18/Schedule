import requests
from bs4 import BeautifulSoup
from datetime import date

url = f"http://www.patriarchia.ru/bu/{date.today()}/"

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

req = requests.get(url, headers=headers)
src = req.text


with open("index.html", "w", encoding="utf-8") as file:
    file.write(src)

with open("index.html", encoding="utf-8") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")

title = soup.title.string
in_day_head = soup.find(class_ = "ln-day-head").text

service_options = soup.find(class_ = "ln-emb-note").text
if service_options[:10] == "Примечание":
    service_options = soup.find(class_ = "ln-emb-note").find_next().find_next().find_next().find_next().text
print(service_options)

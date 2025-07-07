import requests
from bs4 import BeautifulSoup
import pandas as pd

URL: str = "http://www.andrewclem.com/Baseball/Stadium_lists.html"

response = requests.get(URL)
soup = BeautifulSoup(response.content, "html.parser")

rows = []

for table in soup.find_all("table"):
    for p in table.find_all("p", class_="link"):
        for link in p.find_all("a"):
            stadium: str = link.text.strip()
            if stadium not in [row["stadium"] for row in rows]:
                home_link: str = f"http://www.andrewclem.com/Baseball/{link.get("href")}"
                
                content = requests.get(home_link).content
                home_soup = BeautifulSoup(content, "html.parser")
                img_tag = home_soup.find("img", attrs={"name": "stadVers"})
                img_link = f"http://www.andrewclem.com/Baseball/{img_tag["src"]}" if img_tag else None
                rows.append({"stadium": stadium, "home_link": home_link, "img_link": img_link})
    

df: pd.DataFrame = pd.DataFrame(rows, columns=["stadium", "home_link", "img_link"])
df.to_csv("model/stadium_cache/stadium_list.csv", index=False)
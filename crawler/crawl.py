from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import requests
import json
import re
from selenium.common.exceptions import NoSuchElementException
import csv

header = {'User-Agent': ''}
d = webdriver.Chrome('./chromedriver')
d.implicitly_wait(3)
d.get('http://www.melon.com/chart/index.htm')
d.get("http://www.melon.com/chart/search/index.htm")
d.find_element_by_xpath('//*[@id="d_chart_search"]/div/h4[1]/a').click()


for i in range(4, 5):
    # age
    age_xpath = '//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[' + str(i) + ']/span/label'
    age = d.find_element_by_xpath(age_xpath)
    age.click()

    # year
    for i in range(5, 11):
        result = list()

        try:
            year_xpath = '//*[@id="d_chart_search"]/div/div/div[2]/div[1]/ul/li[' + str(i) + ']/span/label'
            year = d.find_element_by_xpath(year_xpath)
            year.click()
            print(year.text)

        except:
            print("year_xpath not found")
            continue
            
        # month
        for i in range(1,13):
            try:
                month_xpath = '//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[' + str(i) + ']/span/label'
                month = d.find_element_by_xpath(month_xpath)
                month.click()
                print(month.text)

            except:
                print("month_xpath not found")
                continue
        
            # week
            for i in range(1,6):
                try:
                    week_xpath = '//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li[' + str(i) + ']/span/label'
                    week = d.find_element_by_xpath(week_xpath)
                    week.click()
                    print(week.text)

                except:
                    print("week_xpath not found")
                    continue
                

                # genre selection
                try:
                    classCd = d.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[2]/span/label')
                except:
                    classCd = d.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li/span/label')
                
                
                classCd.click()
                print(classCd.text)

                # search button
                d.find_element_by_xpath('//*[@id="d_srch_form"]/div[2]/button/span/span').click()
                sleep(10)

                song_ids = d.find_elements_by_xpath('//*[@id="lst50"]/td[4]/div/a')
                song_ids = [re.sub('[^0-9]', '', song_id.get_attribute("href")) for song_id in song_ids]
                ranks = d.find_elements_by_xpath('//*[@id="lst50"]/td[2]/div/span[1]')

                for rank, song_id in zip(ranks, song_ids):
                    sleep(5)
                    print(song_id)

                    req = requests.get('http://www.melon.com/song/detail.htm?songId=' + song_id, headers = header)
                    html = req.text
                    soup = BeautifulSoup(html, "html.parser")

                    title = soup.find(attrs={"class": "song_name"}).text.replace('곡명', '')

                    if '19금' in title:
                        title = title.replace('19금', '')

                    title = re.sub('^\s*|\s+$','', title)
                    
                    singers = re.sub('<[^>]*>|\s|\[|\]', '', str(soup.find('div', class_ = "artist")))

                    album = soup.select('#downloadfrm > div > div > div.entry > div.meta > dl > dd')[0].text
                    date = soup.select('#downloadfrm > div > div > div.entry > div.meta > dl > dd')[1].text
                    genre = soup.select('#downloadfrm > div > div > div.entry > div.meta > dl > dd')[2].text 
                    
                    list_ = singers.split(',')
                    count = len(list_)
                    
                    creator = re.sub('<[^>]*>|\s|\[|\]', '', str(soup.find_all("div", attrs={"class": "entry"})))
                    creator = re.sub('^\s*|\s+$', '', creator)
                    clist = creator.split(',')
                    creator = []
                    for x in clist:
                        if '작사' in x:
                            creator.append(x[:-2])
                    creator = ','.join(creator)        
                    lyric = re.sub('<[^>]*>|\s|\[|\]', ' ', str(soup.find_all(attrs={"class": "lyric"})[0]))
                    lyric = re.sub('^\s*|\s+$', '', lyric)
                    
                    result.append({
                        'year': re.sub('[^0-9]', '', year.text),
                        'rank': rank.text,
                        'title': title,
                        'singers': singers,
                        'album': album,
                        'date' : date,
                        'genre': genre,
                        'creator' : creator,
                        'lyric' : lyric
                        })
                    print("차트 연도:", year.text)
                    print("순위:", rank.text)
                    print("곡 id:", song_id)
                    print("제목:", title)
                    print("아티스트:", singers)
                    print("앨범:", album)
                    print("발매날짜:", date)
                    print("장르:", genre)
                    print("작사:", creator)
                    print("가사:", lyric)
                    print("*_*_*_*_*_*_*_*_*_*_*__*_*_*")

                with open('result_{}.csv'.format{year.text}, 'w') as csvfile:
                    fieldnames = ["차트 연도", "순위", "곡 id", "제목", "아티스트", "앨범", "발매날짜", "장르", "작사", "가사"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for i in len(result):
                        writer.writerow(result[i])
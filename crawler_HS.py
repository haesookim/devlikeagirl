from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import requests
import json
import re
from selenium.common.exceptions import NoSuchElementException
import csv
import os

header = {'User-Agent': ''}

# use incognito mode
option = webdriver.ChromeOptions()
option.add_argument(" - incognito")

# chromedriver 위치 지정 수정
d = webdriver.Chrome(executable_path='/Library/Application Support/Google/chromedriver', chrome_options=option)
d.implicitly_wait(3)
d.get('http://www.melon.com/chart/index.htm')
d.get("http://www.melon.com/chart/search/index.htm")
d.find_element_by_xpath('//*[@id="d_chart_search"]/div/h4[1]/a').click()

# 연도 범위 수정
for i in range(2, 3):
    # age 10년 단위
    age_xpath = '//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[' + str(i) + ']/span/label'
    age = d.find_element_by_xpath(age_xpath)
    age.click()

    # year
    for i in range(1, 11):

        try:
            year_xpath = '//*[@id="d_chart_search"]/div/div/div[2]/div[1]/ul/li[' + str(i) + ']/span/label'
            year = d.find_element_by_xpath(year_xpath)
            year.click()
            print(year.text)

        except:
            print("year_xpath not found")
            continue

        # month
        for i in range(1, 13):
            try:
                month_xpath = '//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[' + str(i) + ']/span/label'
                month = d.find_element_by_xpath(month_xpath)
                month.click()
                print(month.text)

            except:
                print("month_xpath not found")
                continue

            # week
            for i in range(1, 6):
                # weekly save
                result = list()
                try:
                    week_xpath = '//*[@id="d_chart_search"]/div/div/div[4]/div[1]/ul/li[' + str(i) + ']/span/label'
                    week = d.find_element_by_xpath(week_xpath)
                    week.click()
                    print(week.text)

                except:
                    print("week_xpath not found")
                    continue
                # 이미 크롤링된 week라면 다음 week로 넘기기
                if (os.path.isfile('./result_{}_{}.csv'.format(year.text, week.text))):
                    continue

                # genre selection
                try:
                    classCd = d.find_element_by_xpath(
                        '//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[2]/span/label')
                except:
                    classCd = d.find_element_by_xpath(
                        '//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li/span/label')

                classCd.click()
                print(classCd.text)

                # search button
                d.find_element_by_xpath('//*[@id="d_srch_form"]/div[2]/button/span/span').click()
                sleep(10)

                # check whether next_page exists
                next_exist = True
                page_list = ['''"lst50"''']  # initialize with the first page
                try:
                    next_xpath = '//*[@id="frm"]/div[2]/span/a'
                    next_button = d.find_element_by_xpath(next_xpath)
                except:
                    next_exist = False
                if next_exist:
                    page_list.append('''"lst100"''')  # next page

                for page in page_list:
                    song_ids = d.find_elements_by_xpath('//*[@id={}]/td[4]/div/a'.format(page))
                    song_ids = [re.sub('[^0-9]', '', song_id.get_attribute("href")) for song_id in song_ids]
                    ranks = d.find_elements_by_xpath('//*[@id={}]/td[2]/div/span[1]'.format(page))

                    for rank, song_id in zip(ranks, song_ids):
                        sleep(5)
                        print(song_id)

                        #노래가 없을 때의 예외처리 (181012 HS)
                        try:
                            req = requests.get('http://www.melon.com/song/lyrics.htm?songId=' + song_id, headers=header)
                            html = req.text
                            soup = BeautifulSoup(html, "html.parser")

                            title = soup.find(attrs={"class": "song_name"}).text.replace('곡명', '')

                            if '19금' in title:
                                title = title.replace('19금', '')

                            title = re.sub('^\s*|\s+$', '', title)

                            # 가수
                            singers = re.sub('<[^>]*>|\s|\[|\]', '', str(soup.find('div', class_="artist")))

                            album = soup.select('#downloadfrm > div > div > div.entry > div.meta > dl > dd')[0].text
                            date = soup.select('#downloadfrm > div > div > div.entry > div.meta > dl > dd')[1].text
                            genre = soup.select('#downloadfrm > div > div > div.entry > div.meta > dl > dd')[2].text

                            # 작사가
                            creator = re.sub('<[^>]*>|\s|\[|\]', '', str(soup.find_all("div", attrs={"class": "entry"})))
                            creator = re.sub('^\s*|\s+$', '', creator)
                            clist = creator.split(',')
                            creator = []
                            for x in clist:
                                if '작사' in x:
                                    creator.append(x[:-2])
                            creator = ','.join(creator)

                            # 가사
                            # 가사가 없을 시의 예외처리 필요 (181011 by BH)
                            if soup.find_all(attrs={"class": "lyric"}):
                                lyric = re.sub('<[^>]*>|\s|\[|\]', ' ', str(soup.find_all(attrs={"class": "lyric"})[0]))
                                lyric = re.sub('^\s*|\s+$', '', lyric)
                            else:  # 가사 없을 시에는 공백만
                                lyric = ''

                            result.append({
                                'time': re.sub('[^0-9~]', '.', year.text + week.text),
                                'rank': rank.text,
                                'song_id': song_id,
                                'title': title,
                                'singers': singers,
                                'album': album,
                                'date': date,
                                'genre': genre,
                                'creator': creator,
                                'lyric': lyric
                            })
                            print("차트 기간:", year.text + " " + week.text)
                            print("순위:", rank.text)
                            print("곡 id:", song_id)
                            print("제목:", title)
                            print("가수:", singers)
                            print("앨범:", album)
                            print("발매날짜:", date)
                            print("장르:", genre)
                            print("작사:", creator)
                            print("가사:", lyric)
                            print("*_*_*_*_*_*_*_*_*_*_*__*_*_*")
                        except Exception:
                            continue

                    try:
                        next_button.click()
                    except:
                        print("No next page")

                with open('./result_{}_{}.csv'.format(year.text, week.text), 'w') as csvfile:
                    fieldnames = ["time", "rank", "song_id", "title", "singers", "album", "date", "genre", "creator",
                                  "lyric"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for i in range(len(result)):
                        writer.writerow(result[i])
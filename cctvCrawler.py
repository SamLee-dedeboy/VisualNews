import urllib.request, json
import requests
from datetime import datetime
dt = datetime.now() 

def crawl_cctv():
    data = []
    end = False
    for i in range(1,8):
        if(end):
            break
        url = "http://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_" + str(i) +".jsonp?cb=t"
        print("Requiring data from:")
        print(url)
        res =  urllib.request.urlopen(url).read()
        print("Require data Done.")
        res = str(res,'utf-8')[5:-1]
        #print(res)
        #data += json.loads(res)
        result = json.loads(res)
        for news in result['data']['list']:
            if news['focus_date'].split(" ")[0] == dt.strftime("%Y-%m-%d"):
                data.append(news)
            
            else:
                #print(news['focus_date'].split(" ")[0])
                end=True
                break
    print("Saving data into: raw_data\\"+ dt.strftime("%Y%m%d") +".json")
    #with open("raw_data\\20200503.json","w",encoding='utf-8') as f:
    with open("raw_data\\" + dt.strftime("%Y%m%d") +".json","w",encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=4)
    print("Save done.")
crawl_cctv()
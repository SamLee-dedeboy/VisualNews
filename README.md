# VisualNews
## 新聞事件的交互性可視化分析系統

1. 從網上爬取大量的新聞網頁，從中抽取新聞的標題、時間、正文等基本數據作爲原數據.
2. 對正文進行語義分析，抽取其中的句法結構和命名實體（人物，地點，時間）
3. 可視化分析部分：1. 將篩選出的新聞的時序、地理分佈分別可視化。2. 將每個新聞中提到的命名實體根據句法結構組織成圖(Graph)的形式。

### 系統架構：
- 整個系統分爲前端和後端，使用RESTful API格式進行通信。
- 前端框架使用vue.js, 還使用了cystoscape.js, plotly.js, BingMap等第三方庫。
- 後端分爲數據爬取與處理、信息抽取、服務器等模塊。其中信息抽取模塊使用pyltp進行語義分析，服務器模塊使用node.js。

### 用戶界面：
#### 初始界面：
![](https://github.com/SamLee-dedeboy/picturesURL/blob/master/%E6%A1%88%E4%BE%8B%E5%88%86%E6%9E%901.png?raw=true)
#### 搜尋“復工”後出現關於“復工”的新聞列表，以及事件在地圖上的分佈：
![](https://github.com/SamLee-dedeboy/picturesURL/blob/master/%E6%A1%88%E4%BE%8B%E5%88%86%E6%9E%902.png?raw=true)
#### 事件在時間上的分佈：
![](https://github.com/SamLee-dedeboy/picturesURL/blob/master/%E6%A1%88%E4%BE%8B%E5%88%86%E6%9E%903.png?raw=true)
#### 某篇新聞内容的可視化效果：
![](https://github.com/SamLee-dedeboy/picturesURL/blob/master/%E5%86%85%E5%AE%B9%E5%8F%AF%E8%A7%86%E5%8C%96%E5%9B%BE1.png?raw=true)
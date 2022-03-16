# VisualNews: Interactive visual analytics system for news events
## Workflow
1. Extract title, timestamp and contents from web pages on news as dataset.
2. Conduct semantic analysis on the content and extract syntactic structures as well as Name Entities(characters, location, time).
3. Visualization: (1) geographical and temporal distribution of the selected set of news (2) a graph visialization of the extracted syntactic structure, where nodes are named entities and edges are syntactic relations.

## Implementation：
- The front-end is developed with `vue.js`. The visualization components are developed with `cytoscape.js`, `plotly.js` and `BingMap API`. 
- The back-end is developed with `node.js`, and the semetic analysis is conducted with `pyltp`.


## User Interface：
#### Initial Interace：
![](https://github.com/SamLee-dedeboy/picturesURL/blob/master/%E6%A1%88%E4%BE%8B%E5%88%86%E6%9E%901.png?raw=true)
### Geographical Distribution
After searching some keywords, the related news are returned and the geographical distribution is shown below. Each event is represented as a `pin` on the map, and the user can interact with the map to explore more detail about the news. The user can also zoom-in/out to get an overview of the geographical distribution.
![](https://github.com/SamLee-dedeboy/picturesURL/blob/master/%E6%A1%88%E4%BE%8B%E5%88%86%E6%9E%902.png?raw=true)
### Temporal Distribution 
The temporal attribute is represented as a date. On the 'ClockMap', the months are organized as the same order as the time on a clock. Each dot on the ClockMap is a news event. If there are more than one year, then different years will have different radius. This visualization enbales the user to quickly identify temporal patterns within the dataset. For example, the user can easily find that there are more covid-19 cases in winter than in summer. 
![](https://github.com/SamLee-dedeboy/picturesURL/blob/master/%E6%A1%88%E4%BE%8B%E5%88%86%E6%9E%903.png?raw=true)
### News Content visualization
Each node is an extracted named entity. Different node colors represent differnt types of named entity(character, location or time). The edges are created by conducting syntactic analysis on the sentence shown below. 
![](https://github.com/SamLee-dedeboy/picturesURL/blob/master/%E5%86%85%E5%AE%B9%E5%8F%AF%E8%A7%86%E5%8C%96%E5%9B%BE1.png?raw=true)
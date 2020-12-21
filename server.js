var url = require('url');
var util = require('util');
const csv=require('csvtojson');
var fs = require('fs');
var express = require('express');
var bodyParser = require('body-parser');
var http = require('http');
var path = require('path')
var urlencodedParser = bodyParser.urlencoded({ extended: false })
var app = express();

app.use(express.static('public'));

function quiryLocation(place) {

  url="http://dev.virtualearth.net/REST/v1/Locations?q="+place+"&key=AtIgQlLKYNFcVRnLvuCpb3BHRAAQwLNarnwJiEBnhvLiueLRnF6553ioOe9kCMAe"
  console.log("url: ",url)
  http.get(url, (res) => {
    let data = '';
  
    // A chunk of data has been recieved.
    res.on('data', (chunk) => {
      data += chunk;
    });
  
    // The whole response has been received. Print out the result.
    res.on('end', () => {
      data_json = JSON.parse(data)
      console.log(data_json.resourceSets[0].resources[0].point.coordinates)
    });
  
    }).on("error", (err) => {
    console.log("Error: " + err.message);
  });


}
var event_data = new Array()
let jsonFiles = [];
function findJsonFile(dirPath){
    console.log("Directory Path: " + dirPath)
    let files = fs.readdirSync(dirPath);
    files.forEach(function (item, index) {
        let fPath = path.join(dirPath,item);
        let stat = fs.statSync(fPath);
        if(stat.isDirectory() === true) {
            findJsonFile(fPath);
        }
        if (stat.isFile() === true) { 
          jsonFiles.push(fPath);
        }
    });
}
function loadData() {
  for(i in jsonFiles) {
    console.log("Reading data from %s", jsonFiles[i])
    file = path.join(__dirname,jsonFiles[i])
    fs.readFile(file, 'utf-8', function(err,data) {
      if(err) {
        console.log("read data failed")
      } else {
        new_data = JSON.parse(data)
        addGraph(new_data)
        event_data = event_data.concat(new_data)

    }
    })
  }
  console.log("All done.")
}

function addGraph(new_data){

  for(i in new_data) {
    var event = new_data[i]
    var head,index
    if(event.entity_tag_lst.includes("Nv")) {
      index = event.entity_tag_lst.indexOf("Nv")
    } else if (event.entity_tag_lst.includes("Nr")) {
      index = event.entity_tag_lst.indexOf("Nr")
    } else if (event.entity_tag_lst.includes("Ni")) {
      index = event.entity_tag_lst.indexOf("Ni")
    } else if (event.entity_tag_lst.includes("Nh")) {
      index = event.entity_tag_lst.indexOf("Nh")
    } else {
      index = event.entity_tag_lst.indexOf("Ns")

    }
    head = event.entity_lst[index]
    event.graph = new Array()
    //node
    for(i in event.entity_lst) {
      event.graph.push({
        data: {
          id:event.entity_lst[i],
          tag:event.entity_tag_lst[i]}
      })
    }
    for(i in event.time_lst) {
      event.graph.push({
        data: {
          id:event.time_lst[i],
          tag:"time"
        }
      })
    }
    //edge
    edge_id_lst=[]
    for(i in event.relation_lst) {
      event.graph.push({
        data: {
          id: event.relation_lst[i].src + "->" + event.relation_lst[i].dst,
          source: event.relation_lst[i].src,
          target: event.relation_lst[i].dst,
          tag:event.relation_lst[i].tag
        }
      })
      edge_id_lst.push(event.relation_lst[i].src)
      edge_id_lst.push(event.relation_lst[i].dst)

    }
    
    for(i in event.entity_lst) {
      if(i != index && !edge_id_lst.includes(event.entity_lst[i])){
        event.graph.push({
          data: {
            id: head + "->" + event.entity_lst[i],
            source: head,
            target: event.entity_lst[i]
          }
        })
      }
    }
    for(i in event.time_lst) {
      event.graph.push({
        data: {
          id: head + "->" + event.time_lst[i],
          source: head,
          target: event.time_lst[i]
        }
      })
    }
  }
}

findJsonFile('NamedEntityRecognizer/extracted');
loadData()
/*
var jsonObj = csv()
.fromFile("testSample.csv", charset='utf-8')
.then((jsonObj)=>{
    //jsonObj = JSON.stringify(jsonObj)
    jsonObj[0].graph = [ // list of graph elements to start with
        { // node a
          data: { id: 'a' }
        },
        { // node b
          data: { id: 'b' }
        },
        { // edge ab
          data: { id: 'ab', source: 'a', target: 'b' }
        }
      ]
      jsonObj[1].graph = [ // list of graph elements to start with
        { // node a
          data: { id: 'd' }
        },
        { // node b
          data: { id: 'e' }
        },
        { // edge ab
          data: { id: 'de', source: 'd', target: 'e' }
        }
      ]
      //console.log(jsonObj)

    return jsonObj
})
*/
function search(keyword, location, person) {
  var searchResult = new Array()
  for(i in event_data) {
    var event = event_data[i]
    if(location != "null" && person != "null") {
      if(event.entity_lst.includes(location) && event.entity_lst.includes(person)) {
        if(keyword=="null") {
          searchResult.push(event)
        } else if(event.title.includes(keyword) || event.description.includes(keyword)) {
          searchResult.push(event)
        }
      }
    } else if(location != "null" && person == "null") {
      if(event.entity_lst.includes(location)) {
        if(keyword=="null") {
          searchResult.push(event)
        } else if(event.title.includes(keyword) || event.description.includes(keyword)) {
          searchResult.push(event)
        }
      }
    } else if(location == "null" && person != "null") {
      if(event.entity_lst.includes(person)) {
        if(keyword=="null") {
          searchResult.push(event)
        } else if(event.title.includes(keyword) || event.description.includes(keyword)) {
          searchResult.push(event)
        }
      }
    } else if(location == "null" && person == "null") {
      if(keyword=="null") {
        searchResult.push(event)
      } else if(event.title.includes(keyword) || event.description.includes(keyword)) {
        searchResult.push(event)
      }
    }
  
  }
  return searchResult
}
app.get('/news/:keyword/:location/:person', function(req,res) {
    console.log("Get request: /news")
    res.setHeader("Access-Control-Allow-Origin", "*");
    console.log("Searching... Param: %s, %s, %s", req.params["keyword"],req.params["location"],req.params["person"])
    var searchResult = search(req.params["keyword"],req.params["location"],req.params["person"])
    console.log("Search Done. Total: %d", searchResult.length)
    for(var i in searchResult){
      console.log(searchResult[i].coordinate)
    }
    //console.log(searchResult[0].graph)
    //console.log(event_data)
    res.end(JSON.stringify(searchResult))
})
app.get('/index.html', function (req, res) {
    console.log("Get request: %s",req.url)
    res.sendFile( __dirname + "/" + 'index.html');
 })

var server = app.listen(8081, function () {
 
    var host = server.address().address
    var port = server.address().port
   
    console.log("应用实例，访问地址为 http://%s:%s", host, port)
   
  })
app.get('/hobbs-pearson-trials.csv', function(req,res) {
    res.sendfile(__dirname + "/" + "hobbs-pearson-trials.csv")
})
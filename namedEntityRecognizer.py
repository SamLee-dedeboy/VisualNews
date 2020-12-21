import os
import jieba
from pyltp import Segmentor
from pyltp import NamedEntityRecognizer
from pyltp import Postagger
from pyltp import Parser
from pyltp import SentenceSplitter

import requests
import json
import threading
class Relation(object):
    def __init__(self,src,dst,tag):
        self.src = src
        self.dst = dst
        self.type = tag
class Event(object):
    def __init__(self,title,description,url,date,time_lst=[],entity_lst=[],entity_tag_lst=[],relation_lst=[],coordinate=0):
        self.title = title
        self.description = description
        self.url = url
        self.date = date
        self.time_lst = time_lst
        self.entity_lst = entity_lst
        self.entity_tag_lst = entity_tag_lst
        self.relation_lst = relation_lst
        self.coordinate = coordinate
class myLTP(object):
    def __init__(self):
            
        LTP_DATA_DIR = 'ltp_data_v3.4.0'  # ltp模型目录的路径
        cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
        ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 分词模型路径，模型名称为`cws.model`
        pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
        par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')

        self.recognizer = NamedEntityRecognizer() # 初始化实例
        self.recognizer.load(ner_model_path)  # 加载模型
        self.segmentor = Segmentor()
        self.segmentor.load(cws_model_path)
        self.postagger = Postagger() # 初始化实例
        self.postagger.load(pos_model_path)  # 加载模型
        self.parser = Parser() # 初始化实例
        self.parser.load(par_model_path)  # 加载
        #get postags

    def segment(self,text):
        words = list(self.segmentor.segment(text))
        #print(words)
        return words
    def postag(self,words):
        postags = list(self.postagger.postag(words))
        return postags
    def arcs(self,words,postags):
        arcs = self.parser.parse(words, postags)  # 句法分析
        arcs = list(self.parser.parse(words, postags))        #print("HEAD:",head)
        return arcs
    #get time
    def extract_info(self,text):
        words = self.segment(text)
        postags = self.postag(words)
        arcs = self.arcs(words,postags)
        
        #get time
        time_lst = []
        i = 0
        for tag, word in zip(postags, words):
            if tag == 'nt':
                j = i
                while postags[j] == 'nt' or words[j] in ['至', '到']:
                    j += 1
                time_lst.append(''.join(words[i:j]))
            i += 1

        # 去重子字符串的情形
        remove_lst = []
        for i in time_lst:
            for j in time_lst:
                if i != j and i in j:
                    remove_lst.append(i)

        text_time_lst = []
        for item in time_lst:
            if item not in remove_lst:
                text_time_lst.append(item)

        #get entity
        netags = list(self.recognizer.recognize(words, postags))  # 命名实体识别
    
        entity_index = [i for i in range(len(netags)) if netags[i] != 'O']
        print(entity_index)
        entity_words = []
        
        #words = [x for (index,x) in enumerate(words) if index in entity_index]
        #print(words)
        #merge words
        i=0
        tags=[]
        while i < len(entity_index):
            
            if netags[entity_index[i]][0] == "B":
                tags.append(netags[entity_index[i]][2:])
                begin = entity_index[i]
                end = entity_index[i]
                for j in range(begin + 1,len(netags)):
                    i=i+1
                    if netags[j][0] == "E":
                        end = j
                        break
                new_word = "".join(words[begin:end+1])
                entity_words.append(new_word)
                
            else:
                entity_words.append(words[entity_index[i]])
                tags.append(netags[entity_index[i]][2:])
            i+=1

        print(entity_words)
        #print(text_time_lst)
       # print("\n\n\n")
        relation_lst = []
        child_dict_list = self.build_parse_child_dict(words, postags, arcs)
        for index in range(len(postags)):
        # 抽取以谓词为中心的事实三元组
            if postags[index] == 'v':
                child_dict = child_dict_list[index]
                # 主谓宾
                if 'SBV' in child_dict and 'VOB' in child_dict:
                    e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
                    r = words[index]
                    e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                    if e1 not in entity_words:
                        entity_words.append(e1)
                        tags.append("Nr") #node regular
                    if r not in entity_words:
                        entity_words.append(r)
                        tags.append("Nv") #node verb
                    
                    if e2 not in entity_words:
                        entity_words.append(e2)
                        tags.append("Nr")
                    relation_lst.append(Relation(e1,r,"SBV")) # subject-verb
                    relation_lst.append(Relation(r,e2,"VOB")) # verb-object

                    print("主语谓语宾语关系\t(%s, %s, %s)\n" % (e1, r, e2))
                        #out_file.write("主语谓语宾语关系\t(%s, %s, %s)\n" % (e1, r, e2))
                        #out_file.flush()
                # 定语后置，动宾关系
                if arcs[index].relation == 'ATT':
                    if 'VOB' in child_dict:
                        e1 = self.complete_e(words, postags, child_dict_list, arcs[index].head - 1)
                        r = words[index]
                        e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                        temp_string = r+e2
                        if temp_string == e1[:len(temp_string)]:
                            e1 = e1[len(temp_string):]
                        if temp_string not in e1:
                            if e1 not in entity_words:
                                entity_words.append(e1)
                                tags.append("Nr") #node regular
                            if r not in entity_words:
                                entity_words.append(r)
                                tags.append("Nv") #node verb
                            if e2 not in entity_words:
                                entity_words.append(e2)
                                tags.append("Nr")
                            relation_lst.append(Relation(r,e2,"VOB"))  
                            relation_lst.append(Relation(e1,r,"ATT"))  

                            print("定语后置动宾关系\t(%s, %s, %s)\n" % (e1, r, e2))
                               # out_file.write("定语后置动宾关系\t(%s, %s, %s)\n" % (e1, r, e2))
                                #out_file.flush()
                # 含有介宾关系的主谓动补关系
                if 'SBV' in child_dict and 'CMP' in child_dict:
                    #e1 = words[child_dict['SBV'][0]]
                    e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
                    cmp_index = child_dict['CMP'][0]
                    r = words[index] + words[cmp_index]
                    if 'POB' in child_dict_list[cmp_index]:
                        e2 = self.complete_e(words, postags, child_dict_list, child_dict_list[cmp_index]['POB'][0])
                        if e1 not in entity_words:
                            entity_words.append(e1)
                            tags.append("Nr") #node regular
                        if r not in entity_words:
                            entity_words.append(r)
                            tags.append("Nv") #node verb
                        if e2 not in entity_words:
                            entity_words.append(e2)
                            tags.append("Nr")
                        relation_lst.append(Relation(e1,r,"SBV")) # Subject Verb Complement
                        relation_lst.append(Relation(r,e2,"CMP"))
                        print("介宾关系主谓动补\t(%s, %s, %s)\n" % (e1, r, e2))
                            #out_file.write("介宾关系主谓动补\t(%s, %s, %s)\n" % (e1, r, e2))
                            #out_file.flush()
        
        return (entity_words,tags,relation_lst, text_time_lst)
    def build_parse_child_dict(self,words, postags, arcs):
        """
        为句子中的每个词语维护一个保存句法依存儿子节点的字典
        Args:
            words: 分词列表
            postags: 词性列表
            arcs: 句法依存列表
        """
        child_dict_list = []
        #print(list(words), len(words))
        for index in range(len(words)):
            child_dict = dict()
            for arc_index in range(len(arcs)):
                if arcs[arc_index].head == index + 1:
                
                    if arcs[arc_index].relation in child_dict:
                        child_dict[arcs[arc_index].relation].append(arc_index)
                    else:
                        child_dict[arcs[arc_index].relation] = []
                        child_dict[arcs[arc_index].relation].append(arc_index)
            #if child_dict.has_key('SBV'):
            #    print words[index],child_dict['SBV']
            child_dict_list.append(child_dict)
        #print(child_dict_list)
        return child_dict_list

    def complete_e(self,words, postags, child_dict_list, word_index):
        """
        完善识别的部分实体
        """
        child_dict = child_dict_list[word_index]
        prefix = ''
        if 'ATT' in child_dict:
            for i in range(len(child_dict['ATT'])):
                prefix += self.complete_e(words, postags, child_dict_list, child_dict['ATT'][i])
        
        postfix = ''
        if postags[word_index] == 'v':
            if 'VOB' in child_dict:
                postfix += self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
            if 'SBV' in child_dict:
                prefix = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0]) + prefix

        return prefix + words[word_index] + postfix
    def free_ltp(self):
        self.postagger.release()
        self.recognizer.release()  # 释放模型
        self.segmentor.release()   
        self.parser.release()

def getRequest(event):
    place =""
    for (index,tag) in enumerate(event.entity_tag_lst):
        if tag == "Ns":
            place = event.entity_lst[index]
            break
    place = "%20".join(ltp.segment(place))
    url = "http://dev.virtualearth.net/REST/v1/Locations?q="+place+"&key=AtIgQlLKYNFcVRnLvuCpb3BHRAAQwLNarnwJiEBnhvLiueLRnF6553ioOe9kCMAe"
    
    res = requests.get(url)
    print("get response")
    data = json.loads(res.text)
    #print(data["resourceSets"])
    if data["resourceSets"][0]["estimatedTotal"]!=0:
        coordinate = data["resourceSets"][0]["resources"][0]["point"]["coordinates"]
        event.coordinate = coordinate
    if place == "湖北":
        coordinate = data["resourceSets"][0]["resources"][1]["point"]["coordinates"]
        event.coordinate = coordinate
    #print(place,event.coordinate)

def thread(event_lst):
    threads=[]
    for i in range(0,len(event_lst)):
        t = threading.Thread(target=getRequest,args=(event_lst[i],))
        threads.append(t)
    for t in threads:
        t.start()
    print("Started requiring...")
    for t in threads:
        t.join()
    print("All Completed")


ltp = myLTP()
if __name__ == '__main__':
    from datetime import datetime
    dt = datetime.now() 
    fileList=["20200424","20200425","20200426","20200427","20200430","20200501",
    "20200502","20200503","20200504","20200506","20200507","20200508"]
    for filename in fileList:
        with open("raw_data\\" + filename + ".json","r",encoding='utf-8') as f:
            print("Reading data from: raw_data\\" + dt.strftime("%Y%m%d") +".json")
        #with open("raw_data\\" + dt.strftime("%Y%m%d") +".json","r",encoding='utf-8') as f:
            data_lst = json.load(f)
            event_lst = []
            print("Extracting info from raw data...")
            for data in data_lst:
                event = Event(
                    title=data["title"],
                    description=data["brief"],
                    url=data["url"],
                    date=data["focus_date"].split(" ")[0])
                entity_lst, entity_tag_lst, relation_lst, time_lst = ltp.extract_info(data["brief"])
                event.time_lst = time_lst
                event.entity_lst = entity_lst
                event.entity_tag_lst = entity_tag_lst
                event.relation_lst = relation_lst
                event.source="CCTV"
                if "Ns" in entity_tag_lst:
                    event_lst.append(event)
            print("Extract done.")
            print("Creating thread to require coordinate on map info for each news.")
            thread(event_lst)
            event_lst = [event for event in event_lst if event.coordinate != 0]
            print("Saving data to: extracted\\" + filename +".json")
            
            with open("extracted\\" + filename + ".json","w",encoding='utf-8') as f:
            #with open("extracted\\" + dt.strftime("%Y%m%d") +".json","w",encoding='utf-8') as f:
                json.dump(event_lst,f,ensure_ascii=False,indent=4,default=lambda x: x.__dict__)
    ltp.free_ltp()        
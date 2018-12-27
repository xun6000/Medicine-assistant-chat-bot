#coding=utf-8
import  sys
import time
import os
import urllib.request
import json
import requests
import watson_developer_cloud
import re
import copy

import json
import os
import threading
#from watson_developer_cloud import ConversationV1
from flask import request
from flask import Flask, jsonify
from flask import abort
import urllib.request


global d
d={"通用名称":"药品名称","英文名称":"药品名称","拼音名称":"药品名称","成份":"成分","味道":"性状","颜色":"性状","状态":"性状","用量":"用法用量","用法":"用法用量","规格":"规格","适应症":"适应症","有效期":"有效期","不良反应":"不良反应","注意事项":"注意事项/禁忌","禁忌":"注意事项/禁忌","药物相互作用":"药物相互作用","儿童用药":"儿童用药","孕妇及哺乳期妇女用药":"孕妇及哺乳期妇女用药","老年用药":"老年用药","药物过量":"药物过量","贮藏":"贮藏","执行标准":"执行标准","药理毒理":"药理毒理"}

global weidao
weidao=["苦","甜","香"]
global yanse
yanse=["红","橙","黄","绿","青","蓝","紫","黑","褐","红"]
global bidic
bidic=['高血压','高血脂','呼吸道感染','发烧','感冒','咽炎','咳嗽','痛经','偏头痛','肺炎','肺脓肿' \
,'肺结核','慢阻肺','哮喘','肺血栓','气胸','胸腔积液','心力衰竭','心律失常','房早','室早','房颤','室颤', \
'折返','传导阻滞','心脏骤停','心脏性猝死','先心病','高血压','动脉硬化','心瓣膜病','心肌病','心包炎', \
'胃食管反流病','胃炎','肠结核','结核性腹膜炎','溃疡性结肠炎','肠易激综合症','腹泻','肝炎', \
'肝硬化','胰腺炎','消化道出血','急性肾小球肾炎','肾病综合症','尿路感染','贫血','再障','白血病', \
'淋巴瘤','浆细胞病','血小板减少性紫癜','脾亢过敏性紫癜','垂体瘤','巨人症','侏儒症','甲亢','甲减', \
'甲状腺炎','糖尿病','低血糖症','血脂异常','肥胖症','痛风','骨质疏松','水电解质代谢及酸碱平衡失常', \
'类风湿','系统性红斑狼疮','强直性脊柱炎','干燥综合症','系统性硬化病','雷诺病','骨性关节炎','中毒', \
'中暑','溺水','晕动病','高原病'] # 症状和疾病的字典


aaaa="""感冒、肺炎、肺脓肿、肺结核、慢阻肺、哮喘、肺血栓、气胸、胸腔积液、肺癌、睡眠呼吸暂停综合症、呼吸衰竭、呼吸窘迫综合症

、心力衰竭、心律失常、房早、室早、房颤、室颤、折返、传导阻滞、心脏骤停、心脏性猝死、先心病、高血压、动脉硬化、心瓣膜病、心肌病、心包炎

、胃食管反流病、食管癌、胃炎、肠结核、结核性腹膜炎、溃疡性结肠炎、大肠癌、肠易激综合症、腹泻、肝炎、肝硬化、胰腺炎、消化道出血、肝癌

、急性肾小球肾炎、肾病综合症、尿路感染、肾衰竭血液系统：贫血、再障、白血病、淋巴瘤、浆细胞病、血小板减少性紫癜、脾亢过敏性紫癜

、垂体瘤、巨人症"""
aaaa=aaaa.split("、")

global med_glo
global file_glo
med_glo=None
file_glo=None
for i in aaaa:
    bidic.append(i.strip("\n"))
global last_time
last_time=None


global intent
intent=None
global text
text=None
global askdic
askdic=None
global oldmed
oldmed=None


def get_medicine(text):

    body = {"text": text}

    myurl = "http://140.143.150.235:8080/MedicalIE/medical/extractText"
    req = urllib.request.Request(myurl)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(body)
    jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))
    #print(jsondataasbytes)
    response = urllib.request.urlopen(req, jsondataasbytes)

    data = json.loads(response.read().decode('utf-8'))
    print(data)
    entity = []
    for info in data:
        print("hello,",type(info))
        if "type" not in info or info["type"]!="drug":
            continue

        for key in info:
            if key == 'standardname' and (key not in entity) :
                entity.append(info[key])
    #print("药品为:",entity)
    return entity
#print(get_medicine("感冒"))
    #os.system(medicine)

def get_intent(text):
    assistant = watson_developer_cloud.AssistantV1(
        username='apikey',
        password='-SXMsHmxTUE9lpQaOaJZW30BbmJ_0qrcxVgmvatxOhi1',
        version='2018-07-10',

    )

    response = assistant.message(
        workspace_id='cb3d27d4-6dca-469f-8ee8-5f8ce4619b4a',
        input={'text': text
        }
    )
    #print(response['intents'][0]['intent'])



    if len(response['intents'])==0:
        #print("我们不知道您想问哪项内容")
        return
    print("意图为：",response['intents'])
    return response['intents'][0]['intent']

'''jaccard'''
def jaccard_distance(str1,str2):
    si={}
    #for item in list(jieba.cut(str1, cut_all = True)):
    for item in str1:
        #if item in list(jieba.cut(str2, cut_all = True)):
        if item in str2:
            si[item]=1
    n=len(si)
    if n==0:
        return 0
    return n/(len(str1)+len(str2)-n)

'''return dicts which key is the name of drug and the value is the filename'''    
def get_list(text):
    filename_list = os.listdir('data_json/')
    #self.get_medicine()
    drug_filename_dict = {}
    drug_sorted_dict = {}
    sim_list = {}
    for name in filename_list:
        key = name.split('#')[-1]
        key = key[:-5]
        if text in key and ("注射" not in name) and ("皮试" not in name):
            drug_filename_dict[key] = name
    for key in drug_filename_dict:
        sim = jaccard_distance(text,key)
        sim_list[key] = sim
    sort_sims = sorted(sim_list.items(), key=lambda item: -item[1])
    for i in sort_sims:
        name = drug_filename_dict[i[0]]
        drug_sorted_dict[i[0]] = name
    return drug_sorted_dict


def special_people(text):
    a=["儿童","小儿"]
    b=["孕妇","怀孕"]
    c=["老年人","老人"]
    for each in a:
        if each in text:
            return 1
    for each in b:
        if each in text:
            return 2
    for each in c:
        if each in text:
            return 3
    return 0


def find_file(medicine):
    global askdic
    namelists = get_list(medicine[0])
    if len(namelists) == 0:
        return "对不起，我们没有找到对应的说明书"

    if len(namelists) == 1:
        for name in namelists:
            print("我们匹配到：", name)
            filename = namelists[name]
            return filename
    else:
        string = []
        i = 0
        askdic = {}
        for name in namelists:
            string.append(str(i + 1) + ":" + name)
            askdic[str(i + 1)] = namelists[name]
            i += 1
        # print(askdic)
        return "您好我们为您找到了以下药物，请输入您想查询的药物对应的数字:\n"+"\n".join(string)

        #ans = sys.stdin.readline()  # 这里不太好写。。。
        #ans = str(ans[:-1])
        # print(ans)
        # print(type(ans[:-1]))
    #     if ans in askdic:
    #         filename = askdic[ans]
    #     else:
    #         print("数值有误，系统自动选择第一个")
    #         filename = askdic["1"]
    # return filename






def give_the_result():
    # genju file_glo jinxing hou
    global filename
    global intent
    print(intent)
    global bidic
    global file_glo
    if file_glo==None:
        return "对不起，我们没有理解问题.",-1,-1
    filename= "data_json/"+file_glo
    f = open(filename, encoding='utf-8')
    contents = json.load(f)
    f.close()
    if intent != "模糊问题":
        index = d[intent]
        if index in contents:
            print(contents[index])
            # if intent == "味道":
            #     # print("we are here")
            #     for element in weidao:
            #         if element in text:  # element jiushi ku ku在问句当中
            #             start = []
            #             line = re.split(r"；|。|，", contents[index])
            #             # line = re.split(r";|,|。|:", contents[index])
            #             # ["fjeijfi","fejifej","weidao weiku","weiku"]
            #             for i, pos in enumerate(line):
            #                 if element in pos:
            #                     start.append(i)
            #             if len(start) == 0:
            #                 print("我不知道")
            #                 return "我不知道"
            #             elif len(start) == 1:
            #                 print(line[start[0]])
            #                 return line[start[0]]
            #             else:
            #                 print(",".join(line[start[0]:start[-1] + 1]))
            #                 return ",".join(line[start[0]:start[-1] + 1])
            #
            #             break
            #     else:
            #         print(contents[index])
            #         return contents[index]
            # else:
            #     print(contents[index])
            #     return contents[index]
            if intent == '通用名称':
                try:
                    p1 = re.compile(r"(?<=通用名称：).+?(?= 英文名称：)")
                    line = re.findall(p1, contents[index])
                    pos=re.findall(line[0], contents[index])
                    #return("起始位置： ", contents[index].index(line[0]))
                    return(line[0],contents[index].index(line[0]),contents[index].index(line[0][-1]))
                except:
                    return('抱歉，说明书中没有提到该药品的通用名称',-1,-1)

            elif intent == '英文名称':
                try:
                    p1 = re.compile(r"(?<=英文名称：).+?(?= 拼音名称)")
                    line = re.findall(p1, contents[index])
                    pos = re.findall(line[0], contents[index])
                    return (line[0], contents[index].index(line[0]),contents[index].index(line[0][-1]))
                except:
                    return('抱歉，说明书中没有提到该药品的英文名称',-1,-1)

            elif intent == '拼音名称':
                try:
                    p1 = re.compile(r"(?<=拼音名称：).+(?= )")
                    line = re.findall(p1, contents[index])
                    pos = re.findall(line[0], contents[index])
                    return (line[0], contents[index].index(line[0]),contents[index].index(line[0][-1]))

                except:
                    return('抱歉，说明书中没有提到该药品的拼音名称',-1,-1)

            elif intent == "味道":
                try:
                    p1 = re.compile(r"(?<=味).+?(?=。|，)")
                    line = re.findall(p1, contents[index])
                    pos = re.findall(line[0], contents[index])
                    return (line[0], contents[index].index(line[0]),contents[index].index(line[0][-1]))
                except:
                    return('抱歉，说明书中没有提到该药品的味道',-1,-1)

            elif intent == "颜色":
                start = []
                try:
                    line = re.split(r"；|。|，", contents[index])
                    for i, pos in enumerate(line):
                        if "色" in pos:
                            start.append(i)
                    if len(start) == 0:
                        return("抱歉，没找到颜色",-1,-1)
                    elif len(start) == 1:
                        return(line[start[0]],contents[index].index(line[start[0]][0]),contents[index].index(line[start[0]][-1]))
                    else:
                        return(",".join(line[start[0]:start[-1] + 1]),contents[index].index(line[start[0]][0]),contents[index].index(line[start[-1]][-1]))
                except:
                    return('抱歉，说明书中没有提到该药品的颜色',-1,-1)


            else:
                return(contents[index],-1,-1)



        else:
            print("对不起，我们没有找到答案.")
            return ("对不起，我们没有找到答案.",-1,-1)
            # print(setting[index]) # 这样是把一整段都丢给他
            # print(setting[index])
    else:  # 是个模糊问题
        # first find the disease in the sentense
        for element in bidic:
            if element in text:
                word = element
                if word in contents["适应症"]:
                    print("能治")
                    return ("能治",-1,-1)
                if word in contents["注意事项/禁忌"]:
                    print("这是禁忌")
                    return ("这是禁忌",-1,-1)
                print("尚不明确")
                return ("尚不明确",-1,-1)
                break
        else:
            print("我们没找到答案")
            return ("对不起，我们没找到答案",-1,-1)

def findganmao():
    ans = []

    filename_list = os.listdir('data_json/')
    #print(filename_list)
    for name in filename_list:
        if name==".DS_Store":
            continue
        filename = "data_json/" + name
        print(filename)
        f = open(filename, encoding='utf-8',errors='ignore')
        try:
            contents = json.load(f)
            f.close()
            if "适应症" in  contents :
                #print(type(contents["适应症"]))
                if "感冒" in contents["适应症"] or "呼吸道感染" in contents["适应症"] and ("注射" not in name) and ("皮试" not in name):
                    ans.append(name)
                    if len(ans)>=15:
                        break
        except: pass
    print("ans",ans)
    returnlist=[]
    for name in ans:
        # name= fjeifjieji#yaoming.json
        # key=yaoming
        key = name.split('#')[-1]
        # print(key)
        key = key[:-5]
        # if ("注射" not in name) and ("皮试" not in name):
        #
        returnlist.append(key)
    print(returnlist)
    return returnlist,-1,-1
    
def indication_dict(text):
    indication_dicts = {}
    indication_lists = []
    namelists = {}
    filename_list = os.listdir('data_json/')
    for name in filename_list:
        key = name.split('#')[-1]
        key = key[:-5]
        namelists[key] = name
    for key, value in namelists.items():
        filename = 'data_json/' + value
        f = open(filename, encoding='utf-8')
        try:
            contents = json.load(f)
            f.close()
            indication_dicts[key] = contents['适应症']
        except: pass
    for i in bidic:
        if i in text:
            for key,value in indication_dicts.items():
                if i in value:
                    indication_lists.append(key)
                    if len(indication_lists) >= 10:
                        break
    return indication_lists,-1,-1

#findganmao()

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def create_task():
    #global last_time
    global oldmed
    global file_glo
    global intent
    global text
    global askdic
    global content
    global med_glo
    data={}
    if not request.json or not 'text' in request.json:

        return jsonify({'error': "no text"}), 200
    text=request.json['text']# get the query
    print(text)
    if text=="start":
        file_glo=None
        intent=None
        content=None
        askdic=None
        med_glo=None
        data["response"]="请输入您的问题"
        return jsonify(data), 200
    text,option=text.split("___")
    print(text,option)
    if option=="2":
        data["response"] = "we are waiting for the response from DNN"
        #data["Rule-based"]=""
        data["DNN"]="we are waiting for the response from DNN"
        return jsonify(data), 200

    try: # 如果是一个数字
        number=None
        number = int(text)
        print(askdic)
        if text in askdic:
            file_glo = askdic[text]
            #print("we are here to print text")
        else:
            print("数值有误，系统自动选择第一个")
            file_glo = askdic["1"]
        #print("we are at here to check ")
        try:
            data["response"],data["start"],data["end"]=give_the_result()
            data["intent"]=intent
            data["medicine"]=med_glo
        #print("are we here")
        #print("we are here to give the result",data["response"])
            print(data)
            return jsonify(data),200
        except:
            data["response"]="请求超时，请稍后重试"
            return jsonify(data), 200
    except:
        # it is a query
        check = special_people(text)
        # print("check = ",check)
        if check == 0:

            new_intent = get_intent(text)

            if new_intent == None:
                print("我们没理解您的问题，请换一种说法")
                data["response"] = "对不起，我们没理解您的问题，请换一种说法"
                data["intent"] = None
                data["medicine"] = med_glo

                return jsonify(data), 200
        elif check == 1:
            new_intent = "儿童用药"
            print("儿童用药")
        elif check == 2:
            new_intent = "孕妇及哺乳期妇女用药"
            print("孕妇及哺乳期妇女用药")
        elif check == 3:
            new_intent = "老年用药"
            print("老年用药")
        new_medicine = get_medicine(text)
        # if oldmed==None:
        #     oldmed = copy.deepcopy(med_glo)
        # else:
        #     if len(med_glo)!=0:
        #         oldmed = copy.deepcopy(med_glo)

        if  len(new_medicine)==0:
            if "吃什么" in text:
                #print("we are here")
                data["response"], data["start"], data["end"] = indication_dict(text)
                data["intent"] = "查询药物"
                data["medicine"] = None
                return jsonify(data), 200

                
            
               # if "感冒" in text:
               #      data["response"], data["start"], data["end"] = findganmao()
               #      data["intent"] = "问感冒"
               #      data["medicine"] = None
               #
               #      return jsonify(data), 200

                

            if len(new_intent)!=0:
                intent=new_intent
                data["response"], data["start"], data["end"]= give_the_result()
                data["intent"] = intent
                data["medicine"] = med_glo # itshould give the old med_glo
                return jsonify(data), 200
            else:
                data["response"] = "对不起，我们没理解您的问题，请换一种说法"
                data["intent"] = None
                data["medicine"] = med_glo
                return jsonify(data), 200
        elif len(new_medicine)>=2:
            #med_glo = new_medicine[:]
            data["response"] = "这个问题太难了"
            data["intent"] = intent
            data["medicine"] = new_medicine
            return jsonify(data), 200
        else:
            med_glo = new_medicine[:]
            if len(new_intent)!=0:
                intent=new_intent
                data["intent"] = intent
                data["medicine"] = med_glo
            else:
                data["response"] = "对不起，我们没理解您的问题，请换一种说法"
                data["intent"] = None
                data["medicine"] = med_glo
                return jsonify(data), 200

            data["response"] = find_file(new_medicine)[:]
            if "您好我们为您找到了以下药物，请输入您想查询的药物对应的数字:" in data["response"]:
                return jsonify(data), 200
            elif   data["response"]=="我们没有找到对应的说明书":
                return jsonify(data), 200
            else:
                file_glo=data["response"][:]
                data["response"], data["start"], data["end"]= give_the_result()
                data["intent"] = intent
                data["medicine"] = med_glo
                return jsonify(data), 200


if __name__ == '__main__':
    print("Multiple Workspace Ready.")
    app.run(host='0.0.0.0', debug=True, port=int(os.getenv('PORT', 9099)), use_reloader=False, threaded=True)

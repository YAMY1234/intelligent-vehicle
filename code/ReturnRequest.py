import pandas as pd
import datetime as dt
import json
import random
import math
import pymysql

def ReturnRequest(dl_ord,mode):
    if mode == "release" :
        table_name="order_request"
        maxzuoweibuffer = 15  # 15
        maxbusnum = 5  # 5
        zuoweibuffer = 3
    else:
        table_name="order_request_sz_test"
        maxzuoweibuffer = 3  # 15
        maxbusnum = 1  # 5
        zuoweibuffer = 3
    # maxzuoweibuffer 是总的座位数，maxbusnum是总车辆数，zuoweibuffer是单辆车座位数。

    # 处理预约订单数据
    a = str(dl_ord['oId'])
    d = dl_ord['startTime']
    start_time=dt.datetime.strptime(d,"%Y-%m-%d %H:%M:%S")   
    second_order=start_time.hour*3600+start_time.minute*60+start_time.second
    e = dl_ord['ticketNumber']
    ostart=dl_ord['fromId']
    dstart=dl_ord['toId']

    # 构建数据库链接
    conn = pymysql.connect(host="rm-bp164444922wma90vwo.mysql.rds.aliyuncs.com", user="hztest", password="Hjjj0842",
                           db="hztestdb", charset="utf8")
    cur = conn.cursor()

    sql = "select direction from section_info where ostation='" + ostart + "' and dstation='" + dstart + "'"
    cur.execute(sql)
    oddirect = cur.fetchall()
    directionstr = -1
    for raw in oddirect:
        directionstr = raw[0]

    if (zuoweibuffer==0):
       outputstr="暂时没有车辆上线运营，请稍后预约"           
       task_json={"status":302,"direction":int(directionstr),"suggest":str(outputstr)}
       task = json.dumps(task_json, ensure_ascii=False)
       return task
    if (e>zuoweibuffer):
       outputstr="单笔人数过多,您需要减少订单人数至"+str(zuoweibuffer)+"人"           
       task_json={"status":302,"direction":int(directionstr),"suggest":str(outputstr)}
       task = json.dumps(task_json, ensure_ascii=False)
       return task
    if (e==0):
       outputstr="单笔人数为0,您需要新增订单人数"
       task_json={"status":303,"direction":int(directionstr),"suggest":str(outputstr)}
       task = json.dumps(task_json, ensure_ascii=False)
       return task




    sql="select orderod,ordernum,orderlist,secondstime,starttime,charternum from "+table_name+" where date(starttime)=date('"+str(start_time.date())+"')"
    cur.execute(sql)
    results = cur.fetchall()
# 处理历史订单记录时间、人数、订单号、od
    start_time_e=None
    oidnum_e=0   
    oidlist_e=""
    od_e=""
    second_e=-1
    charternum=0
    totalnum=0
    findex=0
    coutDingdan=0
    breakout=-1
    addflag=False

    mintimesel=start_time.hour*18001
    mintimesat=start_time.hour*18001

#运力简单判断，1800取值应为最不利情况调车+本次行程时间
    for raw in results:
        start_time_e=raw [4]      
        second_e=raw [3]
        oidnum_e=raw [1]
        oidlist_e=raw [2]
        od_e=raw [0] 
        charternum=raw[5] 
        if(charternum!=0):
            totalnum+=charternum
            coutDingdan+=1
        if(second_e==second_order and charternum==0): 
            totalnum+=oidnum_e
            coutDingdan+=math.ceil(oidnum_e/3)        
            if(od_e==ostart+"-"+dstart): 
                coutDingdan-=math.ceil(oidnum_e/3)
                coutDingdan+=math.ceil((oidnum_e+e)/3)-1               
                breakout=findex
                addflag=True   
            if((od_e.split("-")[0]==ostart or od_e.split("-")[1]==dstart) and addflag==False):
                mintimesat=0
                breakout=findex   
        if(abs(second_order-second_e)<=1800 and second_e!=second_order and charternum==0):               
            totalnum+=oidnum_e
            coutDingdan+=math.ceil(oidnum_e/3)     
            if(od_e==ostart+"-"+dstart and mintimesel>abs(second_order-second_e) and addflag==False):                
                 breakout=findex
                 mintimesel=second_order-second_e
            if((ostart in od_e or dstart in od_e) and mintimesat>abs(second_order-second_e) and mintimesel==start_time.hour*18001 and addflag==False):
                 mintimesat=second_order-second_e
                 breakout=findex
        findex+=1       
    if(start_time_e!=None):        
        if(totalnum+e>maxzuoweibuffer):
            cur.close()
            conn.close()
            outputstr="当前预约数已满，建议出发前30分钟进行即时下单"
            task_json={"status":301, "direction":int(directionstr),"suggest":str(outputstr)}
            task = json.dumps(task_json, ensure_ascii=False)
            return task
        else:  
            if(coutDingdan>=maxbusnum and breakout==-1):
                cur.close()
                conn.close()
                outputstr="当前预约运能紧张，建议出发前30分钟进行即时下单"           
                task_json={"status":301, "direction":int(directionstr),"suggest":str(outputstr)}
                task = json.dumps(task_json, ensure_ascii=False)
                return task
            else:
                if(coutDingdan>=maxbusnum and breakout!=-1 and mintimesel!=start_time.hour*18001):
                     cur.close()
                     conn.close()
                     outputstr="当前预约运能紧张，建议选择出发时间"+str(results[breakout][4])+"下单"
                     task_json={"status":305, "direction":int(directionstr),"suggest":str(outputstr)}
                     task = json.dumps(task_json, ensure_ascii=False)
                     return task
                if(coutDingdan>=maxbusnum and breakout!=-1 and mintimesel==start_time.hour*18001):  
                     cur.close()
                     conn.close()                  
                     outputstr="当前预约运能紧张，建议选择出发时间"+str(results[breakout][4])+",起始站为"+results[breakout][0]+"下单" 
                     if(addflag==True):      
                          outputstr="当前预约运能紧张"    
                     task_json={"status":305, "direction":int(directionstr),"suggest":str(outputstr)}
                     task = json.dumps(task_json, ensure_ascii=False)
                     return task   
    if(breakout !=-1 and addflag==True):
         oidnum_e=results[breakout][1]+int(e)
         oidlist_e=results[breakout][2]+" "+a  
         od_e=results[breakout][0]
         sql="update "+table_name+" set orderlist='"+str(oidlist_e)+"', ordernum="+str(oidnum_e)+" where orderod='"+str(od_e)+"' and date(starttime)=date('"+str(start_time.date())+"') and secondstime="+str(second_order)+" and charternum=0"
         cur.execute(sql)
         conn.commit()
    else:
         sql="insert into "+table_name+" values (str_to_date('"+str(d)+"','%Y-%m-%d %H:%i:%s'),'"+a+"',"+str(e)+",'"+ostart+"-"+dstart+"',"+str(second_order)+",'"+dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')+"','-1',0)"
         cur.execute(sql)
         conn.commit()

    cur.close()
    conn.close()
    outputstr="预约成功"


    task_json={"status":201, "direction": int(directionstr),"suggest":str(outputstr)}
    task = json.dumps(task_json, ensure_ascii=False)    
    return task

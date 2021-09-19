import pandas as pd
import datetime as dt
import json
import pymysql

def CancelCharterCar(dl_ord,mode):
    #输入数据预处理,进来就是json格式
    #f2 = pd.read_csv("包车信息表.csv",encoding='utf-8')
    if mode=="release":
        table_name="order_request"
    else:
        table_name="order_request_sz_test"

    a = dl_ord['oId']
    d = dl_ord['startTime']
    start_time=dt.datetime.strptime(d,"%Y-%m-%d %H:%M:%S")
    second_order=start_time.hour*3600+start_time.minute*60+start_time.second
    e = dl_ord['charteredBusNum']
    pcout=int(dl_ord['ticketNumber'])
    from_p_id=dl_ord['fromId']
    to_p_id=dl_ord['toId']

    start_time_e=None
    oidnum_e=0   
    o_d_e=[]
    findex=0
    orderid=""
    sql=""

    #if(e!="-1"):
        #findex=0       
        #for raw in f2.itertuples():
            #start_time_e=dt.datetime.strptime(getattr(raw,'c_start_time'),"%Y-%m-%d %H:%M:%S")
            #second_order_e=start_time_e.hour*3600+start_time_e.minute*60+start_time_e.second
            #orderid=getattr(raw,'order_id')
            #if(start_time.year==start_time_e.year and start_time.month==start_time_e.month and start_time.day==start_time_e.day and second_order_e==second_order and a==str(orderid)):                                                 
                  #f2=f2.drop(labels=findex)
                  #break
            #findex+=1
    start_time_e=None
# 构建数据库链接
    conn = pymysql.connect(host="rm-bp164444922wma90vwo.mysql.rds.aliyuncs.com", user="hztest", password="Hjjj0842",db="hztestdb", charset="utf8")
    cur = conn.cursor()    
    sql="select orderod,ordernum,orderlist,secondstime,starttime,charterbus from "+table_name+" where date(starttime)=date('"+str(start_time.date())+"') and orderod='"+ from_p_id+"-"+to_p_id+"' and secondstime="+str(second_order)+" and charterbus='"+e+"'"
    cur.execute(sql)
    results = cur.fetchall()
    for raw in results: 
        start_time_e=raw [4]      
        second_e=raw [3]
        oidnum_e=raw [1]
        oidlist_e=raw [2]
        od_e=raw [0]
        o_d_e=oidlist_e.split(' ') 

        if (o_d_e.count(a)>0):
                o_d_e.remove(a)                
                if(e=="-1"):
                       oidnum_e=oidnum_e-pcout
                if(len(o_d_e)==0):                     
                       sql="delete from "+table_name+" where date(starttime)=date('"+str(start_time.date())+"') and orderod='"+ from_p_id+"-"+to_p_id+"' and secondstime="+str(second_order)+" and charterbus='"+e+"'"
                       cur.execute(sql)
                       conn.commit()
                else:
                       oidlist_e=' '.join(o_d_e)
                       sql="update "+table_name+" set ordernum="+str(oidnum_e)+",orderlist='"+oidlist_e+"' where date(starttime)=date('"+str(start_time.date())+"') and orderod='"+ from_p_id+"-"+to_p_id+"' and secondstime="+str(second_order)+" and charterbus='-1'"
                       cur.execute(sql)
                       conn.commit()
        else:
                start_time_e=None

    if(start_time_e==None):
        outputstr="取消失败，找不到订单预约信息"
        task_json={"status":301,"suggest":str(outputstr)}
        return json.dumps(task_json)
    
    #f2.to_csv('包车信息表.csv',index= False,encoding="utf-8")
    outputstr="取消成功"
    task_json={"status":201,"suggest":str(outputstr)}   
    return json.dumps(task_json)
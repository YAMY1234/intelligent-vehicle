'''
输入：
ticket：订单信息 dict() 
tasks_all: 所有的任务
输出：
task 删除的任务信息
说明：
根据订单删除任务，并且返回信息

'''



def cancel_ticket(tasks_all, ticket):
    oId = ticket['oId']
    for task_id in tasks_all.keys():
        if ticket['oId'] in tasks_all[task_id]['correspondOrderId'].split(','):
            task = tasks_all[task_id]
            #task['correspondOrderId'].pop(task['correspondOrderId'].index(ticket['oId']))
            task['itNumber'] -= int(ticket['ticketNumber'])
            tasks_all[task_id] = task
            return task
    return None        
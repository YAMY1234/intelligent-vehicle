
'''
输入：
tasks_all 所有订单任务的信息
ticket 订单信息
car_info 车辆信息
app_platform_info 站台信息
输出：
return_info 新的任务信息
说明：
拼车信息

'''


def share_car_task_arrange(tasks_all, ticket, car_info, app_platform_info):
    print(ticket)
    begin = ticket['fromId']
    end = ticket['toId']
    return_info = dict()
    for task_id in tasks_all.keys():
        task = tasks_all[task_id]
        if begin in task['travelPlat'] and end in task['travelPlat'] \
            and task['travelPlat'].index(begin) < task['travelPlat'].index(end) \
            and (int(car_info[task['carId']]['seat']) - int(task['itNumber'])) >= int(ticket['ticketNumber']):
            return_info['status'] = 1
            return_info['task'] = dict()
            return_info['task']['travelId'] = task['travelPlat']
            return_info['task']['itNumber'] = task['itNumber'] + ticket['ticketNumber']
            return_info['task']['correspondNumber'] = ticket['orderUserId']
            return_info['task']['correspondSeatId'] = dict()

            if len(task['parkId']):
                task['parkId'] = task['parkId']+begin
            else:
                task['parkId'] = task['parkId'] + ',' + begin
            task['parkId'] = task['parkId'] + ',' + end

            if len(task['parkName']):
                task['parkName'] = task['parkName']+app_platform_info[begin]['p_name']
            else:
                task['parkName'] = task['parkName'] + ',' + app_platform_info[begin]['p_name']
            task['parkName'] = task['parkName'] + ',' + app_platform_info[end]['p_name']

            task['correspondOrderId'] = task['correspondOrderId'] + ',' + ticket['oId']
            task['itNumber'] += int(ticket['ticketNumber'])
            tasks_all[task_id] = task
            return return_info

    return_info['status'] = 0
    return_info['task'] = None
    return return_info
# -*- coding: utf-8 -*-

import requests, re #, datetime


# 在输入的网址上爬取开奖日期、期数、开奖号码、下一次开奖网址，并返回dict
def get_data(target_url = ""):

    # 请求的首部信息
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
    # 例子的url
    # url = 'https://www.js-lottery.com/Article/news/group_id/3/article_id/91912.html' # 目标网页
    url = "https://www.js-lottery.com/Chart/sevenFenBu" # 目标网页
    # if target_url[1:5] != "http":
    #     url = 'https://www.js-lottery.com' + target_url
    # else:
    #     url = target_url[1:].replace("http", "https")
    # print(url)

    # 利用requests对象的get方法，对指定的url发起请求，该方法会返回一个Response对象
    res = requests.get(url, headers=headers)
    # 通过Response对象的text方法获取网页的文本信息，res.text是一个完整的str
    # print(res.text)

    # 将res.text从一整个str拆分成单行
    text_list = res.text.split('\n')

    # # local test only
    # with open("test_res_test_splited.txt", "w", encoding="utf-8") as f:
    #     f.writelines(line + "\n" for line in text_list)
    #     f.close()
    
    res_list_1 = []  # 开奖期数
    res_list_2 = []  # 中奖号码
    for line in text_list:
        # <td class="odd">24055</td>
        res_1 = re.search(r'<td class="odd">([0-9]+)</td>', line)
        if res_1 is not None:
            batch_no_str = res_1.group().replace('<td class="odd">', '').replace('</td>', '')
            batch_no_int = int(batch_no_str)
            res_list_1.append(batch_no_int)
        
        # <td stype="width:160px;">9&nbsp;8&nbsp;6&nbsp;8&nbsp;0&nbsp;4&nbsp;9</td>
        res_2 = re.search(r'<td stype="width:160px;">(([0-9]&nbsp;)+[0-9])</td>', line)
        if res_2 is not None:
            # 将字符串形式的开奖号码转换成list
            lottery_num = res_2.group().replace('<td stype="width:160px;">', '').replace('</td>', '')
            lottery_num_str_list = lottery_num.split('&nbsp;')
            lottery_num_int_list = []
            for s in lottery_num_str_list:
                lottery_num_int_list.append(int(s))
            res_list_2.append(lottery_num_int_list)
    
    if len(res_list_1) != len(res_list_2):
        print("[ERROR] 读取的开奖期数与中奖号码列表大小不一致，请检查网页格式是否有更新：%s" % url)
    # else:
    #     print(res_list_1)
    #     print(res_list_2)
    
    """
    # 搜索其中带有关键信息的行号
    batch_num = '    <title> 中国体育彩票江苏省7位数第'
    date_line = '<p>开奖日期'
    lottery_num_line = '<br/>本期开奖号码'
    end_line = '<div style="padding:10px 0px 10px 0px;">上一篇'
    found_lines = 0
    batch_num_index = -1
    date_line_index = -1
    lottery_num_line_index = -1
    end_line_index = -1

    for i in range(len(text_list)):
        # print(text_list[i])
        if found_lines != 4:
            if re.search(batch_num, text_list[i]) is not None:
                batch_num_index = i
                found_lines += 1
            if re.search(date_line, text_list[i]) is not None:
                date_line_index = i
                found_lines += 1
            if re.search(lottery_num_line, text_list[i]) is not None:
                lottery_num_line_index = i
                found_lines += 1
            if re.search(end_line, text_list[i]) is not None:
                end_line_index = i  # 更新：不再找它的下一行
                # end_line_index = i + 1  # 注意这里实际是找它的下一行
                found_lines += 1
        else:  # 如果四个关键行都找到了，就停止查找
            break

    batch_num_str = text_list[batch_num_index]
    date_line_str = text_list[date_line_index]
    lottery_num_line_str = text_list[lottery_num_line_index]
    end_line_str = text_list[end_line_index]
    # print(batch_num_index, batch_num_str)
    # print(date_line_index, date_line_str)
    # print(lottery_num_line_index, lottery_num_line_str)
    # print(end_line_index, end_line_str)
    """

    # 提取关键信息，写入dict
    data = {}
    # data['current_url'] = url
    # data['batch_no'] = re.findall(r"中国体育彩票江苏省7位数第(.+?)期开奖公告", batch_num_str)[0]
    # data['date'] = re.findall(r"开奖日期：(.+?)日", date_line_str)[0] + '日'
    # 如果直接搜不到，就简单截取最后13个字符（7个数字+6个空格）
    # try:
    #     data['lottery_num'] = re.findall(r"本期开奖号码：(.+?)<br/>", date_line_str)[0]
    # except IndexError:
    #     data['lottery_num'] = lottery_num_line_str.strip()[-13:]

    data['batch_no'] = res_list_1
    data['lottery_num'] = res_list_2

    """
    # 将字符串形式的开奖号码转换成list
    lottery_num_int_list = []
    for i in range(7):
        lottery_num_int_list.append(int(data['lottery_num'].split(' ')[i]))
    data['lottery_num'] = lottery_num_int_list
    # 最后一期开奖页面找不到这一行，会报错IndexError
    try:
        data['next_url'] = re.findall(r'<a href="(.+?)">中国体育彩票', end_line_str)[0]
    except IndexError:
        pass

    # 将文字日期转换为python变量
    def get_week_day(date):
        week_day_dict = {
            0 : '星期一',
            1 : '星期二',
            2 : '星期三',
            3 : '星期四',
            4 : '星期五',
            5 : '星期六',
            6 : '星期日',
        }
        
        day = date.weekday()  # 这里会输出0-6的数字
        return week_day_dict[day]

    date_result = re.search(r'(\d+)年(\d+)月(\d+)日', str(data['date']))
    d_year  = int(date_result.group(1))
    d_month = int(date_result.group(2))
    d_day   = int(date_result.group(3))

    # 构造一个date类的对象（提供整型的年月日即可）
    a = datetime.date(d_year, d_month, d_day)
    # 输出星期几
    data['weekday'] = get_week_day(a)
    # 输出固定长度的日期
    date_format = '%d-%02d-%02d' % (d_year, d_month, d_day)
    """
    
    # 添加文字说明
    # report = '%s %s 第%s期 开奖号码： ' % (date_format, data['weekday'], str(data['batch_no']))
    # for i in range(7):
    #     report += str(data['lottery_num'][i])
    report = []
    for n in range(len(data['batch_no'])):
        report_item = '江苏 第%s期 开奖号码： ' % str(data['batch_no'][n])
        for i in range(7):
            report_item += str(data['lottery_num'][n][i])
        report.append(report_item)
    data['report'] = report

    return data

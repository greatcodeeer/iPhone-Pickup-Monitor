import time
import datetime
import requests
import json
from playsound import playsound


def bbs(s):
    if not is_alarm_on:
        print('[{}] {}'.format(datetime.datetime.now().strftime('%H:%M:%S'), s))


input('欢迎使用iPhone取货预约助手，请合理使用工具\n正在检查环境：\n即将播放预约提示音，按任意键开始...')
sound_alarm = './alarm.mp3'
playsound(sound_alarm)

print('配置特定型号')
# Config State
type_phone = json.load(open('category.json', encoding='utf-8'))
url_param = ['state', 'city', 'district']
config_param = []
dic_param = {}
lst_choice_param = []
print('--------------------------------')
for index, item in enumerate(type_phone):
    print('[{}] {}'.format(index, item))
input_type = int(input('选择型号：'))
choice_type = list(type_phone)[input_type]

print('--------------------------------')
for index, (key, value) in enumerate(type_phone[choice_type].items()):
    print('[{}] {}'.format(index, value))
input_size = int(input('选择尺寸/颜色：'))
code_iphone = list(type_phone[choice_type])[input_size]
select_size = type_phone[choice_type][code_iphone]
input('您的选择：{} {}，按任意键继续...'.format(choice_type, select_size))

print('选择计划预约的地址')
headers = {
    'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    'Referer': 'https://www.apple.com.cn/shop/buy-iphone/iphone-13-pro/{}'.format(code_iphone),
    'DNT': '1',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
}
for step, param in enumerate(url_param):
    print('请稍后...{}/{}'.format(step+1, len(url_param)))
    url = "https://www.apple.com.cn/shop/address-lookup?{}".format('&'.join(lst_choice_param))
    response = requests.request("GET", url, headers=headers, data={})
    response_json = json.loads(response.text)
    result_body = response_json['body']
    result_param = result_body[param]
    if type(result_param) is dict:
        result_data = result_param['data']
        print('--------------------------------')
        for index, item in enumerate(result_data):
            print('[{}] {}'.format(index, item['value']))
        input_index = int(input('请选择序号：'))
        choice_result = result_data[input_index]['value']
        dic_param[param] = choice_result
        lst_choice_param.append('{}={}'.format(param, dic_param[param]))
    else:
        lst_choice_param.append('{}={}'.format(param, result_param))

print('正在加载网络资源...')
url = "https://www.apple.com.cn/shop/address-lookup?{}".format('&'.join(lst_choice_param))
response = requests.request("GET", url, headers=headers, data={})
response_json = json.loads(response.text)
provinceCityDistrict = response_json['body']['provinceCityDistrict']
input('您的选择：{}，按任意键继续...'.format(provinceCityDistrict))

# Loop for checking iPhone status
count = 0
is_alarm_on = False
while True:
    try:
        url = "https://www.apple.com.cn/shop/fulfillment-messages?pl=true&parts.0={}&location={}".format(code_iphone, provinceCityDistrict)
        response = requests.request("GET", url, headers=headers, data={})
        res_text = response.text
        res_json = json.loads(res_text)
        stores = res_json['body']['content']['pickupMessage']['stores']
        is_available = False
        lst_available = []
        print('--------------------------------')
        for item in stores:
            storeName = item['storeName']
            pickupSearchQuote = item['partsAvailability'][code_iphone]['pickupSearchQuote']
            bbs('{} - {}'.format(storeName, pickupSearchQuote))
            if pickupSearchQuote == '今天可取货':
                is_available = True
                lst_available.append(storeName)

        if len(lst_available) > 0:
            if not is_alarm_on:
                is_alarm_on = True
                # Display while iPhone is available
                print('以下直营店预约可用：\n{}\nhttps://www.apple.com.cn/shop/buy-iphone'.format(','.join(lst_available)))
            playsound(sound_alarm)

        if not is_available:
            is_alarm_on = False

    except Exception as err:
        bbs(err)
    count += 1
    if not is_alarm_on:
        bbs('5秒后进行第{}次尝试...'.format(count))
        time.sleep(5)
    else:
        time.sleep(2)

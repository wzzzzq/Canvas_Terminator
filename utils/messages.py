import requests

def send_wechat(title, msg,key):
    token = key
    title = title
    content = msg
    template = 'html'
    url = f"https://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}"
    print(url)
    r = requests.get(url=url)
    print(r.text)

if __name__ == '__main__':
    msg = 'Life is short I use python'
    send_wechat("刷分只因",msg)
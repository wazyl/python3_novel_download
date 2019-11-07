# -*- coding:utf-8 -*-
from tkinter import *
import requests
from bs4 import BeautifulSoup

import os
import time

import io  
import sys 

#改变标准输出的默认编码 
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

# 爬取小说函数
def downlaod_novel():
    # 1.获取用户输入的url小说列表地址
    url = entry.get()

    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
    }
    html = requests.get(url,headers=header).text
    # 3.创建对象，解析网页,获取的s的数据类型成为一个对象，并且显示的html代码格式变得清晰了
    s = BeautifulSoup(html,'lxml')
    #print(s)
    # 3.获取小说标题
    title = s.find('div',id='info').find_all('h1')[0].string
    text.insert(END,'开始下载小说:%s' % title)
    text.see(END)

    # 4. 小说列表   
    novel_dict ={}
    title_dict ={}
    id_list = []
    result = s.find('div',id='list').find_all('a')

    # 拼接各种信息 （笔趣阁列表页标题太坑爹了）
    for novel in result:
    	#print(novel.text)
        novel_sn = novel.text.replace(' ：','：').replace('；','：').split('：')[0].strip('第').strip('章').strip('地').strip('与')
        novel_id = _chinesToDigital(novel_sn)

        id_list.append(novel_id)
        novel_dict[novel_id] = url + novel.get('href')
        title_dict[novel_id] = novel.text.replace(' ：','：').replace('；','：').split('：')[1]

    #由于列表页面有章节杂乱的情况，手动排序
    id_list.sort()

    # 循环各个章节下载小说
    num = 0
    for novel_id in id_list:
    	url = novel_dict[novel_id]
    	name = title_dict[novel_id]
    	html = requests.get(url,headers=header).text
    	soup = BeautifulSoup(html,'lxml')
    	biaoti = '第 ' + str(novel_id) + '章:'+ name + '\n\n'
    	new_content = biaoti + soup.find('div',id='content').get_text().replace('\xa0'*4,'\n\n')

    	# 添加数据到列表框的最后
    	text.insert(END,'正在下载:%s' % name)
    	# 文本框向下滚动
    	text.see(END)
    	# 更新(不更新就一直卡在那，显示同样的内容)
    	text.update()
    	write2file(title, title, new_content)

    	if num % 5000 == 0:
    		time.sleep(0.1)
    	num += 1

def write2file(title, file_name, content):  
    """将小说写入本地文件"""  
    print("%s下载中。。。" % file_name)  
    direction = title + "/" + file_name  
    if not os.path.exists(title):  
        os.mkdir(title)  
    with open(direction + ".txt", 'a+',encoding='utf-8') as f:
        f.write(content)  

#中文数字转换为阿拉伯数字
def _chinesToDigital(text):

	CN_NUM = {
	    u'〇': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'零': 0,
	    u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4, u'伍': 5, u'陆': 6, u'柒': 7, u'捌': 8, u'玖': 9, u'貮': 2, u'两': 2,
	}

	CN_UNIT = {
	    u'十': 10,
	    u'拾': 10,
	    u'百': 100,
	    u'佰': 100,
	    u'千': 1000,
	    u'仟': 1000,
	    u'万': 10000,
	    u'萬': 10000,
	    u'亿': 100000000,
	    u'億': 100000000,
	    u'兆': 1000000000000,
	}

	if text.isdigit():
		return float(text)
	total = 0
	unit = 1  # 表示单位：个十百千
	for i, temp_text in enumerate(reversed(text)):
		if temp_text in CN_NUM:
			val = CN_NUM[temp_text]
		else:
			val = CN_UNIT[temp_text]
                
		if val >= 10 and i == len(text)-1: # # 应对 十三 十四 十*之类
			if val > unit:
				unit = val
				total = total + val
			else:
				unit = unit * val
		elif val >= 10:
			
			if val > unit:
				unit = val
			else:
				unit = unit * val
		else:
			total = total + unit * val
	return total

# 1.创建窗口
root = Tk()
# 2.窗口标题
root.title('笔趣阁小说下载软件')
# 3.窗口大小以及显示位置,中间是小写的x
root.geometry('550x400+550+230')
# 窗口显示位置
# root.geometry('+573+286')
# 4.标签控件
lable = Label(root,text='请输入要下载小说的列表URL:',font=('微软雅黑',10))
lable.grid(row=0,column=0)

# 5.输入控件
entry =Entry(root,font=('微软雅黑',25))
entry.grid(row=0,column=1)

# 6.列表框控件
text = Listbox(root,font=('微软雅黑',16),width=45,height=10)
# columnspan组件所跨月的列数
text.grid(row=1,columnspan=2)
# 7.按钮控件
button = Button(root,text='开始下载',width=10,font=('微软雅黑',10),command=downlaod_novel)
button.grid(row=2,column=0,sticky=W)

button1 = Button(root,text='退出',width=10,font=('微软雅黑',10),command=root.quit)
button1.grid(row=2,column=1,sticky=E)

# 消息循环,显示窗口
root.mainloop()

# coding=utf-8
import os
import shutil
import requests
import img2pdf
from tqdm import tqdm
from zipfile import ZipFile
from PyPDF2 import PdfFileWriter, PdfFileReader
from threading import Thread
from config import Config

headers = {
    'User-Agent': '环球银幕HD 2.2 rv:1.0 (iPad; iOS 12.1.3; zh_CN)'.encode('utf-8'),
    'Host': Config.host,
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip'
}


def make_dir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.mkdir(path)


def download_zip(path, file, file_url):
    make_dir(path)
    r = requests.get(file_url, headers=headers)
    with open(os.path.join(path, file), 'wb') as zip_file:
        zip_file.write(r.content)


def get_zipfile_namelist(path, file):
    with ZipFile(os.path.join(path, file), 'r') as zipObj:
        namelist = zipObj.namelist()
        return namelist


def extract_zipfile(path, file):
    with ZipFile(os.path.join(path, file), 'r') as zipObj:
        infolist = zipObj.infolist()
        if len(infolist) == 2:
            if infolist[0].file_size > infolist[1].file_size:
                zipObj.extract(infolist[0].filename, 'unzip')
            else:
                zipObj.extract(infolist[1].filename, 'unzip')
        elif len(infolist) == 1:
            zipObj.extract(infolist[0].filename, 'unzip')
        else:
            print('压缩文件有误，请检查后重试。' + file)


def convert_img2pdf(path, filename, file):
    with open(os.path.join(path, filename), "wb") as f:
        f.write(img2pdf.convert(file))


# 下载 mix_online.zip
mix_url = 'http://' + Config.host + '/items/' + Config.path + '/mix_online.zip'
download_zip('temp', 'mix_online.zip', mix_url)

# 根据 mix_online.zip 取得分页下载链接
listOfFileNames = get_zipfile_namelist('temp', 'mix_online.zip')
pages = len(listOfFileNames)
if pages > 10:
    print('本期杂志有 %s 页。产生下载链接中……' % (pages - 1))
    download_links = []
    host = headers.get('Host')
    for i in range(1, pages):
        download_links.append('http://%s/items/%s/layout_%s.zip' % (host, Config.path, i))
else:
    print('请检查 mix_online.zip 后重试。')
os.remove(os.path.join('temp', 'mix_online.zip'))

# 下载 layout_X.zip
threads = []
num = 1
print('开始下载分页。')
for link in download_links:
    pass
    file_name = 'layout_' + str(num) + '.zip'
    t = Thread(target=download_zip, args=['temp', file_name, link])
    t.start()
    threads.append(t)
    num += 1

for t in tqdm(threads):
    t.join()
print('下载完成')

# 解压 ZIP
file_list = os.listdir('temp')
print('开始解压文件')
for file in file_list:
    try:
        extract_zipfile('temp', file)
    except:
        print(str(file) + ' 解压失败, 重试中')
        download_zip('temp', file, 'http://' + Config.host + '/items/' + Config.path + '/' + file)
        extract_zipfile('temp', file)
        print(str(file) + ' 解压成功')
print('解压完成')

# 重命名文件，图片转 PDF
file_list = []
for root, dirs, files in os.walk('unzip'):
    if len(dirs) == 0:
        file_list.append(os.path.join(root, files[0]))

print('正在处理分页')
make_dir('pdf')
for file in file_list:
    # P000XXX -> XXX
    # pXXX -> XXX
    page = int(file.split('/')[1].replace('P', '').replace('p', ''))
    # XXX -> XXX.pdf
    filename = str(page) + '.pdf'
    if os.path.splitext(file)[-1] == '.pdf':
        # rename pdf
        os.rename(file, os.path.join('pdf', filename))
    else:
        # 处理图片的情况，一般是封面封底
        convert_img2pdf('pdf', filename, file)

# 合并 pdf
PDF_output = PdfFileWriter()
for i in range(pages - 1):
    WorkPath = 'pdf/' + str(i) + '.pdf'
    PDF_input = PdfFileReader(WorkPath)
    addNext = PDF_input.getPage(0)
    PDF_output.addPage(addNext)
    os.remove(WorkPath)

PDF_output.write(open(Config.path.split('/')[1] + '.pdf', 'wb'))

shutil.rmtree('unzip')
shutil.rmtree('pdf')
shutil.rmtree('temp')
print("合并完成")

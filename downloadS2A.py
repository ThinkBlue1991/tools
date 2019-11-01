import requests
from tqdm import tqdm
import os
import datetime


def download_from_url(uuid_array,count):
    uuid = uuid_array[0]
    file_size = uuid_array[1]
    url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('" + uuid +"')/$value"
    dst = "./" + uuid + '{0}'.format(count) +".zip"
    # print(url)
    # header = {'Authorization': 'Basic eWMwMDczMzM6eWMwMDcwMDk='}
    # response = requests.get(url,headers=header, stream=True) #(1)
    # #
    # file_size = int(response.headers['content-length']) #(2)
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= file_size:  # (4)
        return file_size
    header = {'Range': 'bytes={first_byte}-{file_size}', 'Authorization':
'Basic eWMwMDczMzM6eWMwMDcwMDk='}
    pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True,
desc=dst)
    req = requests.get(url, headers=header, stream=True)
    # (5)
    # print("1")
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)

    pbar.close()
    return file_size



if __name__ == "__main__":
    #from threading import Thread
    #threads = list()
    #for i in range(0,4):
    #    t = Thread(target=download_from_url,args=(i,))
    #    t.start()
    #    threads.append(t)
    #for t in threads: 
    count = 0
    with open('./log','w+') as f:
        while True:
            start = datetime.datetime.now()
            result = download_from_url(["fde76892-08f7-4fb0-b935-e5419ab10d35",1200000000], count)
            end = datetime.datetime.now()
            total_time = end - start
            time_str = "{0}\t{1}\t{2}\t{3}\n".format(count,start,end,total_time)
            f.write(time_str)
            f.flush()
            count += 1


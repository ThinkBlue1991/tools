import etcd3
# from etcd3 import  events
#  event = events()

etcd = etcd3.client(host="192.168.5.41", port=2379,
                    ca_cert="E://ssl/kube-ca.pem",
                    cert_cert="E://ssl/kube-etcd-192-168-5-41.pem",
                    cert_key="E://ssl/kube-etcd-192-168-5-41-key.pem")
print(etcd)

print(etcd.status)
result = etcd.get("/testkey")
print(type(result))
print(result[0])

watch_count = 0
events_iterator, cancel = etcd.watch_prefix("/testkey/")
for event in events_iterator:
    print(event)
    event_str = str(event)
    print(isinstance(event, etcd3.events.PutEvent))
    print("key = %s " % event_str.split(' ')[2].split('=')[1])
    watch_count += 1
    if watch_count > 10:
        cancel()

print("finish")


# import datetime
# import os
# import requests
#
#
# def sort_by_receive_time(all_data):
#     # all_data.sort(key=take_receive_time, reverse=True)
#     sorted_data = sorted(all_data, key=lambda data: data['receiveTime'],
#                          reverse=True)
#
#     return sorted_data
#
#
# def convert(datas):
#     try:
#         metadata_list = list()
#         for data in datas:
#             metadata = dict()
#             metadata['SatelliteID'] = data['satelliteID']
#             metadata['productLevel'] = data['productLevel']
#             metadata['cloudPercent'] = data['cloudAmount']
#             metadata['receiveTime'] = datetime.datetime.strptime(
#                 data['imagingTime'], "%Y-%m-%d %H:%M:%S")
#             metadata['geometry'] = data['geopolygon']
#             metadata['imageGsd'] = data['imageRowGSD']
#             real_path = os.path.join(data['path'], data['imageName']).replace(
#                 '\\', '/')
#             browse_url = ''.join(('https://api.obtdata.com',os.path.join('/', real_path)))
#             metadata['browseFileLocation'] = browse_url
#
#             metadata_list.append(metadata)
#
#         return metadata_list
#     except Exception as ex:
#
#         print(ex)
#         return None


#
# r = requests.get("https://api.obtdata.com/standard/searchforapi?code=%5b111.29150390625, 33.92968762757661,111.29150390625,33.92968762757661,111.81884765625001,35.91129848822746,113.82934570312499,37.04202441635081,116.51000976562501,36.89280138293984,119.12475585937499,35.447246055511485,119.58618164062501,33.178939260581046,117.48779296875001,31.994100723260786,114.78515625,31.36770891512083,111.851806640625,32.10584293285768,111.29150390625,33.92968762757661,%5d&startTime=&endTime=&cloudage=0&satellite=%5bOVS-1A,OVS-1B,OVS-2A%5d&page=0&pagesize=2")

# r = requests.get("https://api.obtdata.com/standard/searchforapi?code=%5b120.82586231878412, 31.76210627887413, 120.82586231878412, 31.4181881402521, 120.48803272894162, 31.4181881402521, 120.48803272894162, 31.76210627887413%5d&startTime=&endTime=&cloudage=1&satellite=%5bGF1, GF2%5d&page=1&pagesize=6")
# r = requests.get("https://api.obtdata.com/standard/searchforapi?code=%5b111.29150390625, 33.92968762757661,111.29150390625,33.92968762757661,111.81884765625001,35.91129848822746,113.82934570312499,37.04202441635081,116.51000976562501,36.89280138293984,119.12475585937499,35.447246055511485,119.58618164062501,33.178939260581046,117.48779296875001,31.994100723260786,114.78515625,31.36770891512083,111.851806640625,32.10584293285768,111.29150390625,33.92968762757661%5d&startTime=&endTime=&cloudage=&satellite=%5bOVS-1B, GF1,OVS-1A,OVS-1B,OVS-2A%5d&page=1&pagesize=6")
# r = requests.get("https://api.obtdata.com/standard/searchforapi?code=%5b107.69897460937499, 34.4793919710481, 105.260009765625, 34.4793919710481, 104.512939453125, 35.89795019335753, 106.88598632812499, 37.09900294387623, 107.69897460937499, 34.4793919710481%5d&startTime=&endTime=&cloudage=&satellite=%5bGF1, GF2, OVS-1A, OVS-1B, OVS-2A, OHS-2A, OHS-2B, OHS-2C, OHS-2D%5d&page=1&pagesize=6")
# r = requests.get("https://api.obtdata.com/standard/searchforapi?code=%5b111.29150390625, 33.92968762757661, 111.81884765625001, 35.91129848822746, 113.82934570312499, 37.04202441635081, 116.51000976562501, 36.89280138293984, 119.12475585937499, 35.447246055511485, 119.58618164062501, 33.178939260581046, 117.48779296875001, 31.994100723260786, 114.78515625, 31.36770891512083, 111.851806640625, 32.10584293285768, 111.29150390625, 33.92968762757661, 111.29150390625, 33.92968762757661%5d&startTime=&endTime=&cloudage=0&satellite=%5b OVS-1A, OVS-1B, OVS-2A, OHS-2A, OHS-2B, OHS-2C, OHS-2D%5d&page=0&pagesize=2")
r = requests.get(
    "https://api.obtdata.com/standard/searchforapi?code=%5b48.691406, -38.959409,153.808594, -38.959409,153.808594, 56.559482,48.691406, 56.559482,48.691406, -38.959409%5d&startTime=&endTime=&cloudage=1&satellite=%5bGF1,GF2,OVS-1A,OVS-1B,OVS-2A,OHS-2A,OHS-2B,OHS-2C,OHS-2D%5d&page=1&pagesize=10")
# print(r)
requests.post()
result_json = r.json()
# print(r.text())
print(len(result_json['data']))
# all_data = result_json['data']
# convert_data = convert(all_data)
# all_data = sort_by_receive_time(convert_data)
#
# print(all_data)
# result_data = result_json['data']
# print(len(result_data))

# domain = "https://api.obtdata.com"
# data_path = "E://obtdata"
#
# for data in result_data:
#
#     real_path = os.path.join(data['path'], data['imageName']).replace('\\', '/')
#     url = ''.join((domain, os.path.join('/', real_path)))
#     print(url)
#     request_data = requests.get(url)
#
#     if request_data.status_code == 200:
#         path = os.path.join(data_path, data['imageName'])
#         with open(path, "wb") as obt_data:
#             obt_data.write(request_data.content)

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


from kubernetes import client, config, watch
from kubernetes.client import V1CephFSVolumeSource, V1LocalObjectReference

config.load_kube_config(config_file='config')
configuration = client.Configuration()

core_v1_api = client.CoreV1Api(client.ApiClient(configuration))
batch_v1_api = client.BatchV1Api(client.ApiClient(configuration))
batch_v1_beta1_api = client.BatchV1beta1Api(client.ApiClient(configuration))
mount_path = "/etc/config/"
init_mount_path = '/etc/config/'


def create_job(name, configmap_name, container_name, container_image,
               container_command, namespace="default", env_vars={}):
    """
    Create a k8 Job Object
    Args:
        name:
        configmap_name:
        container_name:
        container_image:
        container_command:list类型,执行程序的命令，例如：['python','/home/test.py']
        namespace:
        env_vars: 环境变量

    Returns:

    """
    try:
        # Body是对象体
        body = client.V1Job(api_version="batch/v1", kind="Job")

        # 对象需要 Metadata,每个JOB必须有一个不同的名称!
        body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        # 添加 Status
        body.status = client.V1JobStatus()

        # 开始 Template...
        template = client.V1PodTemplateSpec()

        # 在Env中传递Arguments:
        env_list = []
        for env_name, env_value in env_vars.items():
            env_list.append(client.V1EnvVar(name=env_name, value=env_value))

        container = client.V1Container(command=container_command, env=env_list,
                                       image=container_image,
                                       image_pull_policy="IfNotPresent",
                                       name=container_name)

        volume_mount = client.V1VolumeMount(name="config-volume",
                                            mount_path=mount_path)
        container.volume_mounts = [volume_mount]

        config_map = client.V1ConfigMapVolumeSource(name=configmap_name)

        volumes = client.V1Volume(name="config-volume", config_map=config_map)

        template.spec = client.V1PodSpec(containers=[container],
                                         restart_policy='OnFailure',
                                         volumes=[volumes],
                                         node_selector={'gpu': 'true'})

        # 最后，创建V1JobSpec
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600,
                                     template=template)

        response = batch_v1_api.create_namespaced_job(namespace, body,
                                                      pretty=True)

        return True, response
    except Exception as ex:
        print(ex)
        return False, "k8s Job Object creates Failed!"


def create_cron_job(name, configmap_name, init_container_name,
                    init_container_image, init_container_command,
                    container_name, container_image, container_command,
                    schedule, namespace="default", env_vars={}):
    try:
        # Body是对象体
        body = client.V1beta1CronJob(api_version="batch/v1beta1",
                                     kind="CronJob")
        # 对象需要 Metadata,每个JOB必须有一个不同的名称!
        body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        # 添加 Status
        body.status = client.V1beta1CronJobStatus()

        template = client.V1PodTemplateSpec()

        # 在Env中传递Arguments:
        env_list = []
        for env_name, env_value in env_vars.items():
            env_list.append(client.V1EnvVar(name=env_name, value=env_value))

        container = client.V1Container(
            command=container_command, env=env_list,
            image=container_image,
            image_pull_policy="IfNotPresent",
            name=container_name)

        volume_mount = client.V1VolumeMount(name="share-volume",
                                            mount_path=mount_path)
        container.volume_mounts = [volume_mount]
        container.args = [mount_path + '']

        init_container = client.V1Container(command=init_container_command,
                                            image=init_container_image,
                                            image_pull_policy="IfNotPresent",
                                            name=init_container_name)

        init_volume_mount = client.V1VolumeMount(name="config-volume",
                                                 mount_path=init_mount_path)
        init_container.volume_mounts = [volume_mount, init_volume_mount]

        share_volume = client.V1Volume(name="share-volume", empty_dir={})

        config_map = client.V1ConfigMapVolumeSource(name=configmap_name)
        config_map_volume = client.V1Volume(name="config-volume",
                                            config_map=config_map)

        vlor = V1LocalObjectReference(name='ceph-secret')
        cephfs = V1CephFSVolumeSource(
            monitors=['192.168.4.21:6789', '192.168.4.22:6789',
                      '192.168.4.29:6789'], user='admin', secret_ref=vlor,
            path='/k8svolume/ai-algo')
        config_map_volume_1 = client.V1Volume(name='demo-path', cephfs=cephfs)
        config_map_volume.template.spec = client.V1PodSpec(
            active_deadline_seconds=600,
            containers=[container],
            restart_policy='OnFailure',
            volumes=[config_map_volume,
                     share_volume, config_map_volume_1],
            init_containers=[init_container])

        job_template = client.V1beta1JobTemplateSpec()
        job_template.spec = client.V1JobSpec(template=template)

        body.spec = client.V1beta1CronJobSpec(starting_deadline_seconds=600,
                                              job_template=job_template,
                                              schedule=schedule)

        # To make an asynchronous HTTP request
        thread = batch_v1_beta1_api.create_namespaced_cron_job(namespace, body,
                                                               async_req=True,
                                                               pretty=True)
        result = thread.get()

        return True, result

    except Exception as ex:
        print(ex)
        return False, ""


def create_configmap(config_map):
    """
    Create a k8 ConfigMap Object
    Args:
        config_map: json类型

    Returns:

    """
    try:
        namespace = config_map['namespace']
        name = config_map['name']
        data = config_map['data']

        metadata = client.V1ObjectMeta(name=name)
        body = client.V1ConfigMap(data=data, metadata=metadata)

        if body:
            core_v1_api.create_namespaced_config_map(namespace=namespace,
                                                     body=body, pretty=True)

            return True
    except Exception as ex:
        print(ex)
        return False


def delete_cron_job():
    batch_v1_beta1_api.delete_namespaced_cron_job()


def watch_k8s():
    try:
        config.load_kube_config(config_file='config')

        batch_v1 = client.BatchV1Api()

        batch_w = watch.Watch()
        for event in batch_w.stream(batch_v1.list_namespaced_job,
                                    namespace='default'):
            # print(event)
            print(
                "Event: %s %s" % (event['type'], event['object'].metadata.name))
            if event['type'] != "DELETED":
                data = batch_v1.read_namespaced_job_status(
                    name=event['object'].metadata.name, namespace='default')
                print("status=%s" % data.status)

    except Exception as ex:
        print(ex)
    finally:
        batch_w.stop()

    # try:
    #     config.load_kube_config(config_file='config')
    #
    #     core_v1 = client.CoreV1Api()
    #     core_w = watch.Watch()
    #     for event in core_w.stream(core_v1.list_namespaced_pod,
    #                                namespace='default'):
    #         # print(event)
    #         print(
    #             "Event: %s %s" % (event['type'], event['object'].metadata.name))
    #         try:
    #             if event['type'] != "DELETED":
    #                 data = core_v1.read_namespaced_pod_status(
    #                     name=event['object'].metadata.name, namespace='default')
    #                 print("status=%s" % data.status.container_statuses)
    #         except Exception as exception:
    #             print(exception)
    #             pass
    #
    # except Exception as ex:
    #     print(ex)
    # finally:
    #     core_w.stop()

class Test:
    def output(self):
        print("test")


class Test1(Test):
    def output(self):
        print("test1")

class Test2(Test):
    def output(self):
        print("test2")


if __name__ == '__main__':

    test1 = Test1()
    test2 = Test2()
    test1.output()
    test2.output()
    # result = kube_create_job_object(name='kube-job',
    #                                 container_image="job-test:v0.1",
    #                                 container_name="kube-job")

    # config.load_kube_config(config_file='config')
    #
    # configuration = kubernetes.client.Configuration()
    #
    # # api_instance = kubernetes.client.BatchV1Api(
    # #     kubernetes.client.ApiClient(configuration))
    #
    # # api_response = api_instance.create_namespaced_job("default", result,
    # #                                                   pretty=True)
    #
    # api_instance = kubernetes.client.CoreV1Api(
    #     kubernetes.client.ApiClient(configuration))
    # body = kube_create_configmap_object(name="config-map-python-1")
    # api_response_config_map = api_instance.create_namespaced_config_map(
    #     namespace='default', body=body, pretty=True)
    # print(api_response_config_map)

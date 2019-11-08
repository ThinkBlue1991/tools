import json

from kubernetes import client, config
from kubernetes.client import V1PodList, V1Pod, V1ObjectMeta, V1Job, \
    V1OwnerReference, V1ConfigMap

config.load_kube_config(config_file='config')
configuration = client.Configuration()

core_v1_api = client.CoreV1Api(client.ApiClient(configuration))
batch_v1_api = client.BatchV1Api(client.ApiClient(configuration))

mount_path = "/etc/build/data/"


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
        template = client.V1PodTemplate()
        template.template = client.V1PodTemplateSpec()

        # 在Env中传递Arguments:
        env_list = []
        for env_name, env_value in env_vars.items():
            env_list.append(client.V1EnvVar(name=env_name, value=env_value))

        container = client.V1Container(name=container_name,
                                       image=container_image, env=env_list)

        container.command = container_command
        container.image_pull_policy = "IfNotPresent"
        volume_mount = client.V1VolumeMount(name="config-volume",
                                            mount_path=mount_path)
        container.volume_mounts = [volume_mount]

        config_map = client.V1ConfigMapVolumeSource(name=configmap_name)

        volumes = client.V1Volume(name="config-volume", config_map=config_map)

        template.template.spec = client.V1PodSpec(containers=[container],
                                                  restart_policy='Never',
                                                  volumes=[volumes],
                                                  node_selector={'gpu': 'true'})
        # volumes = [volumes])

        # 最后，创建V1JobSpec
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600,
                                     template=template.template)
        response = batch_v1_api.create_namespaced_job(namespace, body,
                                                      pretty=True)
        return True, response
    except Exception as ex:
        print(ex)
        return False, "k8 Job Object creates Failed!"


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


def delete_job_by_name(job_name, namespace):
    try:
        if search_job_by_name(job_name, namespace):
            batch_v1_api.delete_namespaced_job(name=job_name,
                                               namespace=namespace)
            return True
        return False

    except Exception as ex:
        print(ex)
        return False


def search_job_by_name(job_name, namespace):
    jobs = batch_v1_api.list_namespaced_job(namespace=namespace)
    for job in jobs.items:
        if job_name == job.metadata.name:
            return True

    return False


# 先删除pod再删除job
def delete_pod_by_job(job_name, namespace):
    try:
        # 获取job的uid
        job_uid = batch_v1_api.read_namespaced_job(name=job_name,
                                                   namespace=namespace).metadata.uid
        print(job_uid)
        # 获取所有的pod
        pods = core_v1_api.list_namespaced_pod(namespace=namespace)
        for pod in pods.items:
            # 得到pod的owner list
            owner_list = pod.metadata.owner_references
            if owner_list:
                uid_list = [owner.uid for owner in owner_list]
            if job_uid in uid_list:
                core_v1_api.delete_namespaced_pod(name=pod.metadata.name,
                                                  namespace=namespace)
    except Exception as ex:
        print(ex)
        return False


def delete_config_map_by_name(config_name, namespace):
    try:
        config_maps = core_v1_api.list_namespaced_config_map(
            namespace=namespace)

        for config_map in config_maps.items:
            if config_name == config_map.metadata.name:
                core_v1_api.delete_namespaced_config_map(name=config_name,
                                                         namespace=namespace)
    except Exception as ex:
        print(ex)
        return False


if __name__ == '__main__':
    import requests
    requests.get()
    # data = {'path.json': "{'test':1}"}
    # config_map = {"namespace": "default", "name": "config-map-python-zyh",
    #               "data": data}
    # if create_configmap(config_map):
    #     create_job(name="kube-job-zyh", configmap_name="config-map-python-zyh",
    #                container_name="kube-job-zyh",
    #                container_image="job-test:v0.1",
    #                container_command=['python3', '/usr/src/app/test.py'],
    #                namespace="default", env_vars={} )
    # print(delete_job_by_name('cronjob-sample-1571714760', 'default'))
    # delete_pod_by_job('hello-crd-1571822280', 'default')
    # search_job_by_name(job_name=None, namespace='default')
    delete_config_map_by_name(config_name='config-map-5d905d54bf8922c856561428-2019-09-08', namespace='illegal-building-inspection')

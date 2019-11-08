from kubernetes import client, config
from kubernetes.client import V1LocalObjectReference, V1CephFSVolumeSource

config.load_kube_config(config_file='E:\VScodeProject\GlobalViewer\k8s\config')
configuration = client.Configuration()

core_v1_api = client.CoreV1Api(client.ApiClient(configuration))
batch_v1_api = client.BatchV1Api(client.ApiClient(configuration))
batch_v1_beta1_api = client.BatchV1beta1Api(client.ApiClient(configuration))
mount_path = "/etc/build/data/"
mount_path_ceph = "/etc/ceph/"


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
                                         volumes=[volumes])

        # 最后，创建V1JobSpec
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600,
                                     template=template)

        response = batch_v1_api.create_namespaced_job(namespace, body,
                                                      pretty=True)

        return True, response
    except Exception as ex:
        print(ex)
        return False, "k8 Job Object creates Failed!"


def create_job_with_init(name, configmap_name, init_container_name,
                         init_container_image, init_container_command,
                         container_name, container_image,
                         container_command, cephfs_path, namespace="default",
                         env_vars={}):
    """
    Create a k8 Job Object with InitContainer
    Args:
        name:
        configmap_name:
        init_container_name:
        init_container_image:
        init_container_command:list类型,执行程序的命令，例如：['python3','run.py']
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

        volume_mount = client.V1VolumeMount(name="config-volume",
                                            mount_path=mount_path)

        # 在Env中传递Arguments:
        env_list = []
        for env_name, env_value in env_vars.items():
            env_list.append(client.V1EnvVar(name=env_name, value=env_value))

        init_container = client.V1Container(command=init_container_command,
                                            env=env_list,
                                            image=init_container_image,
                                            image_pull_policy="IfNotPresent",
                                            name=init_container_name)

        init_volume_mount = client.V1VolumeMount(name="config-volume",
                                                 mount_path=mount_path)
        init_container.volume_mounts = [volume_mount]

        container = client.V1Container(command=container_command, env=env_list,
                                       image=container_image,
                                       image_pull_policy="IfNotPresent",
                                       name=container_name)
        volume_mount_ceph = client.V1VolumeMount(name="ceph-volume",
                                                 mount_path=mount_path_ceph)

        secret_ref = V1LocalObjectReference(name='ceph-secret')

        cephfs = V1CephFSVolumeSource(
            monitors=['192.168.4.21:6789', '192.168.4.22:6789',
                      '192.168.4.29:6789'], user='admin', secret_ref=secret_ref,
            path=cephfs_path)

        volume_ceph = client.V1Volume(name='ceph-volume', cephfs=cephfs)

        container.volume_mounts = [volume_mount, volume_mount_ceph]

        config_map = client.V1ConfigMapVolumeSource(name=configmap_name)

        volumes = client.V1Volume(name="config-volume", config_map=config_map)

        template.spec = client.V1PodSpec(containers=[container],
                                         restart_policy='OnFailure',
                                         volumes=[volumes, volume_ceph],
                                         init_containers=[init_container])

        # 最后，创建V1JobSpec
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600,
                                     template=template)

        response = batch_v1_api.create_namespaced_job(namespace, body,
                                                      pretty=True)

        return True, response
    except Exception as ex:
        print(ex)
        return False, "k8 Job Object creates Failed!"


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
                                                 mount_path=mount_path)
        init_container.volume_mounts = [init_volume_mount, volume_mount]

        share_volume = client.V1Volume(name="share-volume", empty_dir={})

        config_map = client.V1ConfigMapVolumeSource(name=configmap_name)
        config_map_volume = client.V1Volume(name="config-volume",
                                            config_map=config_map)

        template.spec = client.V1PodSpec(active_deadline_seconds=600,
                                         containers=[container],
                                         restart_policy='OnFailure',
                                         volumes=[config_map_volume,
                                                  share_volume],
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


if __name__ == "__main__":
    data = {'path.json': "{'test':1}", "path2.json": "{'test2':2}"}
    config_map = {"namespace": "default", "name": "config-map-python-1",
                  "data": data}
    if create_configmap(config_map):
        create_job_with_init(name="kube-job-1",
                             configmap_name="config-map-python-1",
                             init_container_name="kube-initjob-1",
                             init_container_image="hub.geovis.io/isphere/gdal-python3-base",
                             init_container_command=['cat',
                                                     '/etc/build/data/path.json'],
                             container_name="kube-job-1",
                             container_image="hub.geovis.io/isphere/gdal-python3-base",
                             container_command=['sleep',
                                                '10000'],
                             cephfs_path='/k8svolume/ai-algo/',
                             namespace="default", env_vars={})

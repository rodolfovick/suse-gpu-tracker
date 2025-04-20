import os
import kopf
import logging
import kubernetes
import yaml

GPU_TRACKER_OBJ = 'gputracker-obj.yml'


@kopf.on.create('Node', labels={'node-type': 'gpu-node'})
def create_fn(spec, name, namespace, logger, **kwargs):
    """
    Handle new Nodes with node-type equals to gpu-node. If no suse-gpu-tracker obj 
    is created, create a new one. Otherwise, just add the new gpu-node to the list.
    """

    path = os.path.join(os.path.dirname(__file__), GPU_TRACKER_OBJ)
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=name)
    data = yaml.safe_load(text)

    dynamicClient = kubernetes.dynamic.DynamicClient(kubernetes.client.ApiClient())
    resource = dynamicClient.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    object = resource.create(body=data, namespace=namespace)

    logger.info(f"GPU Tracker created: {object}")


@kopf.on.delete('Node', labels={'node-type': 'gpu-node'})
def delete_fn(spec, name, namespace, logger, **kwargs):
    """
    Handle the delete of Nodes with node-type equals to gpu-node. If there are more gpu-node to 
    suse-gpu-tracker, just remove from list. Otherwise, delete suse-gpu-tracker.
    """

    dynamicClient = kubernetes.dynamic.DynamicClient(kubernetes.client.ApiClient())
    resource = dynamicClient.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    object = resource.get(name='suse-gpu-tracker', namespace=namespace)
    resource.delete(name='suse-gpu-tracker', namespace=namespace)

    logger.info(f"GPU Tracker deleted: {object}")
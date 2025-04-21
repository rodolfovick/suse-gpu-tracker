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

    logger.info(f'::: NAME {name}')

    dynamicClient = kubernetes.dynamic.DynamicClient(kubernetes.client.ApiClient())
    resource = dynamicClient.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    objectList = resource.get(namespace=namespace)

    if not objectList.items:
        path = os.path.join(os.path.dirname(__file__), GPU_TRACKER_OBJ)
        tmpl = open(path, 'rt').read()
        text = tmpl.format(name=name)
        data = yaml.safe_load(text)
        object = resource.create(body=data, namespace=namespace)
        logger.info(f"GPU Tracker created: {object}")
    else:
        object = resource.get(name='suse-gpu-tracker', namespace=namespace)
        gpuNodesList = object.gpu_nodes.split(', ')
        gpuNodesList.append(name)
        gpuNodes = ', '.join(gpuNodesList)
        object = resource.patch(body={'gpu_nodes': gpuNodes}, name='suse-gpu-tracker', 
                       namespace=namespace, content_type='application/merge-patch+json')
        logger.info(f"GPU Tracker updated (create): {object}")
        

@kopf.on.delete('Node', labels={'node-type': 'gpu-node'})
def delete_fn(spec, name, namespace, logger, **kwargs):
    """
    Handle the delete of Nodes with node-type equals to gpu-node. If there are more gpu-node to 
    suse-gpu-tracker, just remove from list. Otherwise, delete suse-gpu-tracker.
    """

    logger.info(f'::: NAME {name}')

    dynamicClient = kubernetes.dynamic.DynamicClient(kubernetes.client.ApiClient())
    resource = dynamicClient.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    object = resource.get(name='suse-gpu-tracker', namespace=namespace)

    gpuNodesList = object.gpu_nodes.split(', ')
    gpuNodesList.remove(name)

    if not gpuNodesList:
        resource.delete(name='suse-gpu-tracker', namespace=namespace)
        logger.info(f"GPU Tracker deleted: {object}")
    else:
        gpuNodes = ', '.join(gpuNodesList)
        object = resource.patch(body={'gpu_nodes': gpuNodes}, name='suse-gpu-tracker', 
                                namespace=namespace, content_type='application/merge-patch+json')
        logger.info(f"GPU Tracker updated (delete): {object}")
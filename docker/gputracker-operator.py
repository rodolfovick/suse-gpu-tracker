import kopf
import kubernetes


GPU_TRACKER_NAME = 'suse-gpu-tracker'


def __newGpuTracker(name):
    """
    Create a new manifest for GPUTracker kind with name suse-gpu-tracker, 
    adding the new node to the list of gpu_nodes.
    """

    return {
        'apiVersion': 'suse.tests.dev/v1',
        'kind': 'GPUTracker',
        'gpu_nodes': name,
        'metadata': {'name': GPU_TRACKER_NAME}
    } 


def __addGpuNode(list, name):
    """
    Add a new node to gpu_nodes list.
    """

    gpuNodesList = list.split(', ')
    gpuNodesList.append(name)
    return ', '.join(gpuNodesList)


def __removeGpuNode(list, name):
    """
    Remove a node from gpu_nodes list.
    """

    gpuNodesList = list.split(', ')
    gpuNodesList.remove(name)
    return ', '.join(gpuNodesList)


@kopf.on.create('Node', labels={'node-type': 'gpu-node'})
def create_fn(spec, name, namespace, logger, **kwargs):
    """
    Handle new Nodes with node-type equals to gpu-node. If no suse-gpu-tracker obj 
    is created, create a new one. Otherwise, just add the new gpu-node to the list.
    """

    logger.info(f'::: CREATE NAME {name}')

    dynamicClient = kubernetes.dynamic.DynamicClient(kubernetes.client.ApiClient())
    resource = dynamicClient.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    objectList = resource.get(namespace=namespace)

    if not objectList.items:
        data = __newGpuTracker(name)
        object = resource.create(body=data, namespace=namespace)
        logger.info(f"GPU Tracker created: {object}")
    else:
        object = resource.get(name=GPU_TRACKER_NAME, namespace=namespace)
        gpuNodes = __addGpuNode(object.gpu_nodes, name)
        object = resource.patch(body={'gpu_nodes': gpuNodes}, name=GPU_TRACKER_NAME, 
                       namespace=namespace, content_type='application/merge-patch+json')
        logger.info(f"GPU Tracker updated (create): {object}")
 

@kopf.on.delete('Node', labels={'node-type': 'gpu-node'})
def delete_fn(spec, name, namespace, logger, **kwargs):
    """
    Handle the delete of Nodes with node-type equals to gpu-node. If there are more gpu-node to 
    suse-gpu-tracker, just remove from list. Otherwise, delete suse-gpu-tracker.
    """

    logger.info(f'::: DELETE NAME {name}')

    dynamicClient = kubernetes.dynamic.DynamicClient(kubernetes.client.ApiClient())
    resource = dynamicClient.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    object = resource.get(name=GPU_TRACKER_NAME, namespace=namespace)
    gpuNodes = __removeGpuNode(object.gpu_nodes, name)

    if not gpuNodes:
        resource.delete(name=GPU_TRACKER_NAME, namespace=namespace)
        logger.info(f"GPU Tracker deleted: {object}")
    else:
        object = resource.patch(body={'gpu_nodes': gpuNodes}, name=GPU_TRACKER_NAME, 
                                namespace=namespace, content_type='application/merge-patch+json')
        logger.info(f"GPU Tracker updated (delete): {object}")


@kopf.on.update('Node', field='metadata.labels.node-type', old='gpu-node')
def update_fn(spec, name, namespace, logger, **kwargs):
    """
    Handle the delete of Nodes with node-type equals to gpu-node. If there are more gpu-node to 
    suse-gpu-tracker, just remove from list. Otherwise, delete suse-gpu-tracker.
    """

    logger.info(f'::: UPDATE NAME {name}')

    dynamicClient = kubernetes.dynamic.DynamicClient(kubernetes.client.ApiClient())
    resource = dynamicClient.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    object = resource.get(name=GPU_TRACKER_NAME, namespace=namespace)
    gpuNodes = __removeGpuNode(object.gpu_nodes, name)

    if not gpuNodes:
        resource.delete(name=GPU_TRACKER_NAME, namespace=namespace)
        logger.info(f"GPU Tracker deleted: {object}")
    else:
        object = resource.patch(body={'gpu_nodes': gpuNodes}, name=GPU_TRACKER_NAME, 
                                namespace=namespace, content_type='application/merge-patch+json')
        logger.info(f"GPU Tracker updated (delete): {object}")
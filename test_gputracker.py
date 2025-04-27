from kubernetes import config, dynamic
from kubernetes.client import api_client
from kubernetes.client.api import core_v1_api

from time import sleep

def create_gpu_node(name):
    data = {
        'apiVersion': 'v1',
        'kind': 'Node',
        'metadata': {
            'name': '',
            'labels': {
                'name': '',
                'node-type': '',
            }
        }
    }

    data['metadata']['name'] = name
    data['metadata']['labels']['name'] = name
    data['metadata']['labels']['node-type'] = 'gpu-node'

    client = api_client.ApiClient(configuration=config.load_kube_config())
    api = core_v1_api.CoreV1Api(client)
    api.create_node(body=data)
    sleep(1)


def create_simple_node(name):
    data = {
        'apiVersion': 'v1',
        'kind': 'Node',
        'metadata': {
            'name': '',
            'labels': {
                'name': '',
            }
        }
    }

    data['metadata']['name'] = name
    data['metadata']['labels']['name'] = name

    client = api_client.ApiClient(configuration=config.load_kube_config())
    api = core_v1_api.CoreV1Api(client)
    api.create_node(body=data)
    sleep(1)


def patch_gpu_node(name):
    data = {
        'metadata': {
            'labels': {
                'node-type': 'gpu-node'
            }
        }
    }

    client = api_client.ApiClient(configuration=config.load_kube_config())
    api = core_v1_api.CoreV1Api(client)
    api.patch_node(name=name, body=data)
    sleep(1)


def patch_simple_node(name):
    data = [{ "op": "remove", "path": "/metadata/labels/node-type"}]

    client = api_client.ApiClient(configuration=config.load_kube_config())
    api = core_v1_api.CoreV1Api(client)
    api.patch_node(name=name, body=data)
    sleep(1)


def delete_gpu_node(name):
    client = api_client.ApiClient(configuration=config.load_kube_config())
    api = core_v1_api.CoreV1Api(client)
    api.delete_node(name=name)
    sleep(1)


def get_gpu_nodes():
    client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_kube_config())
    )
    api = client.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    gt = api.get(name='suse-gpu-tracker', namespace='default')
    return gt.gpu_nodes.split(', ')


def get_node_list():
    client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_kube_config())
    )
    api = client.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    list = api.get(namespace='default')
    return list.items


### ------------------------------------------------------------------------------------ ###


def test_one_node():
    """
    test_one_node: validate the create and delete of a gpu-node node.
    """

    name = 'gpu-ai'

    create_gpu_node(name)
    gpu_nodes = get_gpu_nodes()
    assert name in gpu_nodes

    delete_gpu_node(name)
    gpu_node_list = get_node_list()
    assert not gpu_node_list


def test_multiple_node():
    """
    test_multiple_node: validate the create and delete of ten gpu-node node.
    """

    for i in range(0, 10):
        name = 'gpu-ai-' + str(i)
        create_gpu_node(name)
        gpu_nodes = get_gpu_nodes()
        assert name in gpu_nodes

    for i in range(0, 9):
        name = 'gpu-ai-' + str(i)
        delete_gpu_node(name)
        gpu_nodes = get_gpu_nodes()
        assert name not in gpu_nodes

    name = 'gpu-ai-9'
    delete_gpu_node(name)
    gpu_node_list = get_node_list()
    assert not gpu_node_list


def test_patch_one_node():
    """
    test_patch_one_node: validate the patch of a node. This test: 
    - creates a node without gpu-node;
    - patches it to add gpu-node;
    - patches it to remove gpu-node;
    - patches it to add gpu-node;
    - patches it to remove gpu-node;
    - finally, delete the node;
    """
    
    name = 'gpu-ai'

    create_simple_node(name)
    gpu_node_list = get_node_list()
    assert not gpu_node_list

    patch_gpu_node(name)
    gpu_nodes = get_gpu_nodes()
    assert name in gpu_nodes

    patch_simple_node(name)
    gpu_node_list = get_node_list()
    assert not gpu_node_list

    patch_gpu_node(name)
    gpu_nodes = get_gpu_nodes()
    assert name in gpu_nodes

    patch_simple_node(name)
    gpu_node_list = get_node_list()
    assert not gpu_node_list

    delete_gpu_node(name)


def test_patch_multiple_node():
    """
    test_patch_multiple_node: validate the patch of 10 nodes. This test: 
    - creates a node without gpu-node;
    - patches it to add gpu-node;
    - patches it to remove gpu-node;
    - patches it to add gpu-node;
    - patches it to remove gpu-node;
    - finally, delete the node;
    """

    for i in range(0, 10):
        name = 'gpu-ai-' + str(i)
        create_simple_node(name)
        gpu_node_list = get_node_list()
        assert not gpu_node_list

    for i in range(0, 10):
        name = 'gpu-ai-' + str(i)
        patch_gpu_node(name)
        gpu_nodes = get_gpu_nodes()
        assert name in gpu_nodes

    for i in range(0, 9):
        name = 'gpu-ai-' + str(i)
        patch_simple_node(name)
        gpu_nodes = get_gpu_nodes()
        assert name not in gpu_nodes

    name = 'gpu-ai-9'
    patch_simple_node(name)
    gpu_node_list = get_node_list()
    assert not gpu_node_list

    for i in range(0, 10):
        name = 'gpu-ai-' + str(i)
        patch_gpu_node(name)
        gpu_nodes = get_gpu_nodes()
        assert name in gpu_nodes

    for i in range(0, 9):
        name = 'gpu-ai-' + str(i)
        patch_simple_node(name)
        gpu_nodes = get_gpu_nodes()
        assert name not in gpu_nodes

    name = 'gpu-ai-9'
    patch_simple_node(name)
    gpu_node_list = get_node_list()
    assert not gpu_node_list

    for i in range(0, 10):
        name = 'gpu-ai-' + str(i)
        delete_gpu_node(name)
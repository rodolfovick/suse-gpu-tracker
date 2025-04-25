from kubernetes import config, dynamic
from kubernetes.client import api_client

from time import sleep

def create_gpu_node(name, client):
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

    api = client.resources.get(api_version="v1", kind="Node")
    api.create(body=data, namespace='default')
    sleep(1)


def create_simple_node(name, client):
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

    api = client.resources.get(api_version="v1", kind="Node")
    api.create(body=data, namespace='default')
    sleep(1)


def patch_gpu_node(name, client):
    data = {
        'metadata': {
            'labels': {
                'node-type': 'gpu-node'
            }
        }
    }

    api = client.resources.get(api_version="v1", kind="Node")
    api.patch(name=name, body=data, namespace='default')
    sleep(1)


def patch_simple_node(name, client):
    data = {
        "op": "remove", 
        "path": "/metadata/labels/node-type"
    }

    api = client.resources.get(api_version="v1", kind="Node")
    api.patch(name=name, body=data, namespace='default', type='json')
    sleep(1)


def delete_gpu_node(name, client):
    api = client.resources.get(api_version="v1", kind="Node")
    api.delete(name=name, namespace='default')
    sleep(1)


def get_gpu_nodes(client):
    api = client.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    gt = api.get(name='suse-gpu-tracker', namespace='default')
    return gt.gpu_nodes.split(', ')


def get_node_list(client):
    api = client.resources.get(api_version='suse.tests.dev/v1', kind='GPUTracker')
    list = api.get(namespace='default')
    return list.items


### ------------------------------------------------------------------------------------ ###


def test_one_node():
    client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_kube_config())
    )

    name = 'gpu-ai'

    create_gpu_node(name, client)
    gpu_nodes = get_gpu_nodes(client)
    assert name in gpu_nodes

    delete_gpu_node(name, client)
    gpu_node_list = get_node_list(client)
    assert not gpu_node_list

def test_multiple_node():
    client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_kube_config())
    )

    for i in range(0, 10):
        name = 'gpu-ai-' + str(i)
        create_gpu_node(name, client)
        gpu_nodes = get_gpu_nodes(client)
        assert name in gpu_nodes

    for i in range(0, 9):
        name = 'gpu-ai-' + str(i)
        delete_gpu_node(name, client)
        gpu_nodes = get_gpu_nodes(client)
        assert name not in gpu_nodes

    name = 'gpu-ai-9'
    delete_gpu_node(name, client)
    gpu_node_list = get_node_list(client)
    assert not gpu_node_list


def __test_patch_one_node():
    client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_kube_config())
    )

    name = 'gpu-ai'
    create_simple_node(name, client)

    gpu_node_list = get_node_list(client)
    assert not gpu_node_list

    patch_gpu_node(name, client)
    gpu_nodes = get_gpu_nodes(client)
    assert name in gpu_nodes

    patch_simple_node(name, client)
    gpu_node_list = get_node_list(client)
    assert not gpu_node_list

    patch_gpu_node(name, client)
    gpu_nodes = get_gpu_nodes(client)
    assert name in gpu_nodes

    patch_simple_node(name, client)
    gpu_node_list = get_node_list(client)
    assert not gpu_node_list

    delete_gpu_node(name, client)
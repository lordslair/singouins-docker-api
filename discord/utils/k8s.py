# -*- coding: utf8 -*-

import discord
import re

from kubernetes        import client, config
from kubernetes.stream import stream
from loguru            import logger


def load_config(env):
    if env == 'dev':
        try:
            config.load_kube_config(f"/etc/k8s/{env}/kubeconfig.yaml")
        except Exception as e:
            msg = f'K8s conf load KO (env:{env}) [{e}]'
            logger.error(msg)
            embed = discord.Embed(
                description=msg,
                colour=discord.Colour.red()
            )
            return {'success':   False,
                    'embed':     embed,
                    'namespace': None}
        else:
            return {'success':   True,
                    'embed':     None,
                    'namespace': 'singouins-dev'}
    elif env == 'prod':
        try:
            config.load_kube_config(f"/etc/k8s/{env}/kubeconfig.yaml")
        except Exception as e:
            msg = f'K8s conf load KO [{e}]'
            logger.error(msg)
            embed = discord.Embed(
                description=msg,
                colour=discord.Colour.red()
            )
            return {'success':   False,
                    'embed':     embed,
                    'namespace': None}
        else:
            return {'success':   True,
                    'embed':     None,
                    'namespace': 'singouins'}
    else:
        msg = (f"K8s unknown environement. "
               f"Should be ['test','prod'] (env:{env})")
        logger.warning(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return {'success':   False,
                'embed':     embed,
                'namespace': None}


def get_k8s_pod_list(ctx: discord.AutocompleteContext):
    ret = load_config(ctx.options["env"])
    if ret['success']:
        namespace = ret['namespace']
    else:
        return None

    try:
        pods = client.CoreV1Api().list_namespaced_pod(namespace)
    except Exception as e:
        msg = f'K8s Query KO [{e}]'
        logger.error(msg)
        return None
    else:
        db_list = []
        for pod in pods.items:
            db_list.append(
                discord.OptionChoice(pod.metadata.name)
                )
        return db_list


def k8s_status(env, verbose):
    # K8s conf loading
    ret = load_config(env)
    if ret['success']:
        namespace = ret['namespace']
    else:
        return ret['embed']

    try:
        pods = client.CoreV1Api().list_namespaced_pod(namespace)
    except Exception as e:
        logger.error(f'K8s Query KO [{e}]')
        return None
    else:
        logger.trace(f'K8s Pods Query OK (namespace:{namespace})')
        return pods


def k8s_backup_logs(env):
    # K8s conf loading
    ret = load_config(env)
    if ret['success']:
        namespace = ret['namespace']
    else:
        return ret['embed']

    try:
        pod = client.CoreV1Api().list_namespaced_pod(
            namespace,
            label_selector="name=backup"
            )

        """
        log = client.CoreV1Api().read_namespaced_pod_log(
            name=pod.items[0].metadata.name,
            since_seconds=86400,
            namespace=namespace,
            )
        """

        exec_stdout = stream(
            client.CoreV1Api().connect_get_namespaced_pod_exec,
            pod.items[0].metadata.name,
            namespace,
            command="/etc/periodic/daily/cron-status-sh",
            stderr=True, stdin=False,
            stdout=True, tty=False
            )

    except Exception as e:
        logger.error(f'K8s Query KO [{e}]')
        return None
    else:
        logger.trace(f'K8s Pods Query OK (namespace:{namespace})')
        return exec_stdout


def k8s_deployer(env):
    # K8s conf loading
    ret = load_config(env)
    if ret['success']:
        namespace = ret['namespace']
    else:
        return ret['embed']

    try:
        pod = client.CoreV1Api().list_namespaced_pod(
            namespace,
            label_selector="name=nginx"
            )

        exec_stdout = stream(
            client.CoreV1Api().connect_get_namespaced_pod_exec,
            pod.items[0].metadata.name,
            namespace,
            container='sep-backend-nginx-deployer',
            command=['/etc/periodic/daily/cron-deployer-sh'],
            stderr=True, stdin=False,
            stdout=True, tty=False
            )
    except Exception as e:
        logger.error(f'K8s Query KO [{e}]')
        return None
    else:
        logger.trace(f'K8s Pods Query OK (namespace:{namespace})')
        # We use regex to remove potential ANSI color codes from exec_stdout
        return re.sub(r'\033\[(\d|;)+?m', '', exec_stdout)


def k8s_kill_pod(env, podname):
    # K8s conf loading
    ret = load_config(env)
    if ret['success']:
        namespace = ret['namespace']
    else:
        return ret['embed']

    try:
        # We try to kill the found pod
        client.CoreV1Api().delete_namespaced_pod(podname, namespace)
    except Exception as e:
        logger.warning(f'K8s Kill KO ({namespace}:{podname}) [{e}]')
        return None
    else:
        logger.trace(f'K8s Kill OK ({namespace}:{podname})')
        return True


if __name__ == '__main__':
    print(k8s_backup_logs('prod'))

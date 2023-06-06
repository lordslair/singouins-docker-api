# -*- coding: utf8 -*-

import discord
import re

from kubernetes        import client, config
from kubernetes.stream import stream
from loguru            import logger


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
    if not ret['success']:
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


def load_config(env):
    if env == 'dev':
        try:
            config.load_kube_config(f"/etc/k8s/{env}/kubeconfig.yaml")
        except Exception as e:
            msg = f'K8s conf load KO (env:{env}) [{e}]'
            logger.error(msg)
            return {
                'success': False,
                'embed': discord.Embed(
                    description=msg,
                    colour=discord.Colour.red()
                    ),
                'namespace': None,
                }
        else:
            return {
                'success': True,
                'embed': None,
                'namespace': 'singouins',
                }
    elif env == 'prod':
        try:
            config.load_kube_config(f"/etc/k8s/{env}/kubeconfig.yaml")
        except Exception as e:
            msg = f'K8s conf load KO [{e}]'
            logger.error(msg)
            return {
                'success': False,
                'embed': discord.Embed(
                    description=msg,
                    colour=discord.Colour.red()
                    ),
                'namespace': None,
                }
        else:
            return {
                'success': True,
                'embed': None,
                'namespace': 'singouins',
                }
    else:
        msg = (
            f"K8s unknown environement. "
            f"Should be ['test','prod'] (env:{env})"
            )
        logger.warning(msg)
        return {
                'success': False,
                'embed': discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                'namespace': None,
                }

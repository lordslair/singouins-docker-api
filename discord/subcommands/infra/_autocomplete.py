# -*- coding: utf8 -*-

import discord

from kubernetes        import client
from loguru            import logger

from .__k8stools       import load_config


def get_k8s_pod_list(ctx: discord.AutocompleteContext):
    ret = load_config(ctx.options["env"])
    if ret['success']:
        namespace = ret['namespace']
    else:
        return []

    try:
        pods = client.CoreV1Api().list_namespaced_pod(namespace)
    except Exception as e:
        logger.error(f'K8s Query KO [{e}]')
        return []
    else:
        db_list = []
        for pod in pods.items:
            db_list.append(discord.OptionChoice(pod.metadata.name))
        return db_list

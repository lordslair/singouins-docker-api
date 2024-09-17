# -*- coding: utf8 -*-

import os

from loguru import logger
from prometheus_client import Gauge

# Prometheus metrics
THREAD_COUNT_TOTAL = Gauge('thread_count_total', 'Number of threads (total)')
THREAD_COUNT_FUNGUS = Gauge('thread_count_fungus', 'Number of Fungus threads')
THREAD_COUNT_SALAMANDER = Gauge('thread_count_salamander', 'Number of Salamander threads')

# APP variables
API_ENV = os.environ.get("API_ENV", None)
INSTANCE_PATH = f'ai-instance-{API_ENV.lower()}'
CREATURE_PATH = f'ai-creature-{API_ENV.lower()}'

logger.debug(f"API_ENV: {API_ENV}")
logger.debug(f"INSTANCE_PATH: {INSTANCE_PATH}")
logger.debug(f"CREATURE_PATH: {CREATURE_PATH}")

# Resolver variables
RESOLVER_HOST = os.environ.get("RESOLVER_HOST", 'resolver-svc')
RESOLVER_PORT = os.environ.get("RESOLVER_PORT", 3000)
RESOLVER_URL  = f'http://{RESOLVER_HOST}:{RESOLVER_PORT}'
RESOLVER_CHECK_SKIP = os.environ.get("RESOLVER_CHECK_SKIP")

logger.debug(f"RESOLVER_HOST: {RESOLVER_HOST}")
logger.debug(f"RESOLVER_PORT: {RESOLVER_PORT}")
logger.debug(f"RESOLVER_URL: {RESOLVER_URL}")
logger.debug(f"RESOLVER_CHECK_SKIP: {RESOLVER_CHECK_SKIP}")

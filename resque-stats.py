# collectd-resque-plugin - resque-stats.py
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; only version 2 of the License is applicable.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# Authors:
#   Stephen Craton <scraton at gmail.com>
#
# About this plugin:
#   This plugin uses collectd's Python plugin to record Resque information.
#
# collectd:
#   http://collectd.org
# Redis:
#   http://redis.googlecode.com
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml

import collectd
import redis

# Redis connection information. Override in config by specifying the appropriate keys.
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB   = 0

# Resque information. Override in config by specifying the appropriate keys.
RESQUE_PREFIX = 'resque'
RESQUE_STATS  = ['failed','processed']

# General plugin options.
VERBOSE_LOGGING = False

def fetch_stats():
  """Connect to the Redis server and request the Resque stats."""
  try:
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    log_verbose('Connect to Redis at %s:%s' % (REDIS_HOST, REDIS_PORT))
  except socket.error, e:
    collectd.error('resque_stats plugin: Error connecting to Redis at %s:%s - %r' % (REDIS_HOST, REDIS_PORT, e))
    return None

  # Collect basic stats that we can read direct from Redis.
  stats_keys = map(lambda stat: '%s:stat:%s' % (RESQUE_PREFIX, stat), RESQUE_STATS)
  stats_vals = r.mget(stats_keys)
  stats = dict(zip(stats_keys, stats_vals))

  return stats

def configure_callback(conf):
  """Configure the script based on collectd callback"""
  global REDIS_HOST, REDIS_PORT, REDIS_DB, RESQUE_PREFIX, VERBOSE_LOGGING
  for node in conf.children:
    if node.key == 'Host':
      REDIS_HOST = node.values[0]
    elif node.key == 'Port':
      REDIS_PORT = int(node.values[0])
    elif node.key == 'Db':
      REDIS_DB = int(node.values[0])
    elif node.key == 'Prefix':
      RESQUE_PREFIX = node.values[0]
    elif node.key == 'Verbose':
      VERBOSE_LOGGING = bool(node.values[0])
    else:
      collectd.warning('resque_stats plugin: Unknown config key: %s' % node.key)
  log_verbose('Configured with host=%s, port=%s' % (REDIS_HOST, REDIS_PORT))

def dispatch_value(stats, key, type, type_instance=None):
    """Read a key from info response data and dispatch a value"""
    if key not in stats:
      collectd.warning('resque_stats plugin: Stat key not found: %s' % key)
      return

    if not type_instance:
        type_instance = key

    value = int(stats[key])
    log_verbose('Sending value: %s=%s' % (type_instance, value))

    val = collectd.Values(plugin='resque_stats')
    val.type = type
    val.type_instance = type_instance
    val.values = [value]
    val.dispatch()

def read_callback():
  """Collect Resque stats for collectd callback"""
  log_verbose('Read callback called')
  stats = fetch_stats()

  if not stats:
    collectd.error('resque_stats plugin: No stats received')
    return

  # send high-level values
  dispatch_value(stats, '%s:stat:processed' % RESQUE_PREFIX, 'counter', 'jobs.processed')
  dispatch_value(stats, '%s:stat:failed' % RESQUE_PREFIX, 'counter', 'jobs.failed')
  dispatch_value(stats, '%s:stat:processed' % RESQUE_PREFIX, 'gauge', 'jobs.total-processed')
  dispatch_value(stats, '%s:stat:failed' % RESQUE_PREFIX, 'gauge', 'jobs.total-failed')

def log_verbose(msg):
  if not VERBOSE_LOGGING:
    return
  collectd.info('resque_stats plugin [verbose]: %s' % msg)

# Register callbacks
collectd.register_config(configure_callback)
collectd.register_read(read_callback)

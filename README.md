collectd-resque-plugin
======================

Simple [collectd](http://collectd.org/) python plugin for gathering [resque](https://github.com/resque/resque) stats.

The only data captured currently includes:

* Total processed jobs (gauge)
* Total failed jobs (gauge)
* Processed jobs (counter)
* Failed jobs (counter)

Installation
------------

1. Install dependencies (see below).
1. Copy `resque-stats.py` to `/opt/collectd/lib/collectd/plugins/python` (or wherever you store your plugins).
1. Configure the plugin (see below).
1. Restart collectd.

Dependencies
------------

[redis-py](https://github.com/andymccurdy/redis-py) is required for this plugin to work. You can install it via the [README](https://github.com/andymccurdy/redis-py/blob/master/README.rst) or do the following:

```
sudo pip install redis
```

Configuration
-------------

Add the following to your collectd config, or modify your existing config.

```
<LoadPlugin python>
  Globals true
</LoadPlugin>

<Plugin python>
  ModulePath "/opt/collectd/lib/collectd/plugins/python"
  Import "resque_stats"

  <Module resque_stats>
    Host "localhost"
    Port 6379
    Db 0
    Prefix "resque"
    Verbose false
  </Module>
</Plugin>
```

* `Host` - The host of your redis server. Default: `localhost`
* `Port` - The port of your redis server. Default: `6379`
* `Db` - Redis database that resque is using. Default: `0`
* `Prefix` - Prefix of your resque keys. Default: `resque`
* `Verbose` - Display verbose logging from the plugin. Useful for troubleshooting. Default: `false`

Wishlist
--------

1. Report jobs by queue.
1. Report pending jobs and pending jobs by queue.
1. Report number of workers and active workers.

Contributing
------------

Firstly, thank you! I'd really appreciate, as well as the community, any improvements you can provide. Here's how you can help:

1. Fork this repository.
1. Create a topic branch - `git checkout -b my-awesome-feature`
1. Push to your branch - `git push origin my-awesome-feature`
1. Create a pull request from your branch.
1. That's it!

Special Thanks
--------------

Thanks to [powdahound/redis-collectd-plugin](https://github.com/powdahound/redis-collectd-plugin) for a great example of a collectd python plugin, of which this is based off.

WIP

# What is Anna-Molly?

Anna-Molly is a scalable system to collect metric data for dynamic monitoring. 

* It can:

  - Recieve metrics from Carbon and store the relevent metrics.   
  - Analyze them with one of the available plugin algorithms.   
  - Push the analysis to graphite.   
  - Trigger Events based on the results of the algorithm.   


Anna-Molly has two components.   
    1. Collector  
    2. Task Runner  


* The collector is responsible for receiving the Metrics from a Spout (Metric-Source) and pushing it a Sink.

* The Task-Runner is a celery encapsulated task, that invokes algorithm plugins that then work with the data from the Sink. The plugins can be algorithms, supporting tasks, event handlers or others.


**A word of Caution:**
  This is a work in progress. There are a number of moving parts in Anna-Molly. which makes configuration and setup slightly tricky. You can follow the setup guide below. In case you run into issues in setting it up. Write to us.


# What do I need?
Python (2.6, 2.7)

##Dependencies

  `sudo apt-get install -y build-essential python-pip r-base python-celery redis-server automake`

  `sudo pip -r /opt/anna-molly/requirements.txt`



# Getting Started.

## First Steps

**Assumption:**
  You have a carbon relaying pickled metrics to a destination host:port.

- Bring up the Vagrant Box   
`vagrant up`   

- Configure the collector.json at `/opt/anna-molly/`   
You can use the `/opt/anna-molly/collector.json` as a template.   
Instructions on setting-up the collector config can be found in the sections below.   

- Start the Collector   
`/opt/anna-molly/bin/collector.py --config /opt/anna-molly/config/collector.json`   

We should now have metrics being pushed to RedisSink.   
Verify this issuing `redis-cli -p 6379 monitor`

### Setup Task-Runner/Celery

Configure the `analyzer.json` at `/opt/anna-molly/`   
You can use the `/opt/anna-molly/analyzer.json` as a template.   
Instructions on setting-up the analyzer config can be found in the sections below.   

* Start Task-Runner/Celery   
  `celery -A app worker` from `/opt/anna-molly/lib/`   

* Start Scheduler   
  `celeryd --beat --scheduler=scheduler` from `/opt/anna-molly/utils/scheduler.py`   


# Terminology

## Spout

Metric data source. It is exclusively used by the Collector Daemon to receive the data and push it to the Sink.   

### Implementations:

  1. Carbon Asynchronous TCP Pickle Spout

## Sink

A duplex interface to read and write data.
- Collector writes the data to the sink.      
- Tasks read data from the sink.   
- Tasks can also write to sink.   

### Implementations:

  1. RedisSink   
  2. GraphiteSink (Write Only)   

## Models

Class definitions that dicate how Time Series data is stored in the Sink or used by the tasks.

`TimeSeriesTuple`
For simplicity, data is stored and processed around as TimeSeriesTuple. 


## Base Task

Base Task module is an abstract class that all plugins inherit from. It can setup the necessary resources/connections for the plugin.   
And exposes a `run` method which is implement by the plugins.  
   

## Collector Daemon

Collector Daemon receives data from a Spout and pushes it to a Sink.   
Metrics of interest can be configured in `config/collector.json`. See configuration section below for details.   

* Collector uses Spouts to listen/receive data.   
* The data received if in whitelist is then instanciated to the configured model and pushed into the Sink.   


## Task Runner

The task runner is an encapsulated Celery Task.   
Any Plugin in the `/plugins. folder can be invoked by the task-runner as a task.   


### Poll Tasks

Poll tasks are special tasks that are invoked by the scheduler to identify and trigger the actual Algorithm Task.


## Plugins

Plugins inherit from the BaseTask module and are responsible for setting up resources required for the Plugin to run. It also implements the run method which is invoked by the task-runner.   


# Configuration

There are three configuration files:
1. collector.json: Used by the `Collector`.   
2. analyzer.json: Used by `Celery/BaseTask`.   
3. services.json: Used by Plugins for algorithm specific configuration.   

Note: The configuration needs to be simplified and will be worked on shortly.

## collector.json
### Router
```json
{
  "router": {
    "blacklist": [
      "MX",
      "osys.*"
    ],
    "whitelist": {
      ".*": [
        {
          "RedisTimeStamped": {
            "ttl": 10000
          }
        }
      ]
    }
  }
}
```
Config for routing/modeling the metrics. 
- Blacklist (Array)
Metrics blacklisted are rejected.
- Whitelist (Object)
Metrics that match a whitelist are instantiaed in the models specified in the config. Other metrics are ignored.

Metrics that have N models configured, will have N objects stored in the Sink.

### Writer
```json
{
  "writer": {
    "RedisSink": {
      "host": "127.0.0.1",
      "port": 6379,
      "db": 3,
      "pipeline_size": 50
    }
  }
}
```
Needs Sink 

### Listener
```json
{
  "listener": {
    "CarbonAsyncTcpSpout": {
      "host": "0.0.0.0",
      "port": 2014
    }
  }
}
```
Needs Spout and Spout configuration.

## analyzer.json
Celery
```json
{
  "celery": {
    "broker": {
      "host": "redis://127.0.0.1:6379/0"
    },
    "backend": {
      "host": "redis://127.0.0.1:6379/2"
    },
    "time_limit": "120"
  }
}```
Basic Celery configuration. Can be used with a broker/backend of your choice. Refer Celery Docs for more information.

MetricSink
```json
{
  "metric_sink": {
    "RedisSink": {
      "host": "127.0.0.1",
      "port": 6379
    }
  }
}
```
MetricSink is input the Sink from which the plugins will fetch the Metric data for analysis. It must provide configuration specific to the Sink implementation

OutputSink
```json
{
  "output_sink": {
    "GraphiteSink": {
      "host": "storage.metrics.foo.com",
      "port": 2003,
      "url": "graphite.foo.com"
    }
  }
}
```
The plugins push the result data into the OutputSink.

Algorithms.
Refer the [wiki](https://github.com/trademob/anna-molly/wiki).

# Datacenter-Load-Balance

## How to configure the testbed
All configuration files are in [testbed-conf/conf](https://github.com/baiwei0427/Datacenter-Load-Balance/tree/master/testbed-conf/conf). 

First, you need to log in 4 switches ([ToR 1](https://github.com/baiwei0427/Datacenter-Load-Balance/blob/master/testbed-conf/conf/tor1.txt), [ToR 2](https://github.com/baiwei0427/Datacenter-Load-Balance/blob/master/testbed-conf/conf/tor2.txt), [Core 1](https://github.com/baiwei0427/Datacenter-Load-Balance/blob/master/testbed-conf/conf/core1.txt) and [Core 2](https://github.com/baiwei0427/Datacenter-Load-Balance/blob/master/testbed-conf/conf/core2.txt)) to configure routing table and ECN. ToR 1, ToR 2, Core 1 and Core 2 can be accessed from sing040, sing041, sing042 and sing043, respectively. 


Then, you need to log in sing040 - sing51 (12 hosts in total) to configure IP addresses, routing table and ARP table. The configuration commands are shown in [testbed-conf/conf/end_host.txt](https://github.com/baiwei0427/Datacenter-Load-Balance/blob/master/testbed-conf/conf/end_host.txt) 


## How to set up the traffic generator


## How to install XPath 

## How to run experiments

import threading
import os
import Queue

def worker():
    while True:
        try:
			j = q.get(block = 0)
        except Queue.Empty:
            return
        #Make directory to save results
        os.system('mkdir '+j[1])
        os.system(j[0])

q = Queue.Queue()

flow_tot = 100000
link_rate = 10
mean_link_delay = 0.000001
host_delay = 0.000020
loads = [0.4, 0.6, 0.8]
connections_per_pair = 2
mean_flow_size = 1711250
flow_cdf = 'CDF_dctcp.tcl'

packet_size = 1460
queue_size = 333
ecn_thresh = 60

init_window = 10
rto_min = 0.005
dupack_thresh = 10
enable_flowbender = True
flowbender_t = 0.05
flowbender_n = 1

fattree_k = 6
topology_x = 2

ns_path = '/home/wei/load_balance/ns-allinone-2.35/ns-2.35/ns'
sim_script = 'fattree_empirical.tcl'

for load in loads:
    scheme = 'ecmp'
    if enable_flowbender == True:
        scheme = 'flowbender'

    # directory name: [workload]_[LB scheme]_[load]
    directory_name = 'websearch_%s_%d' % (scheme, int(load * 100))
    # simulation command
    cmd = ns_path + ' ' + sim_script + ' '\
        + str(flow_tot) + ' '\
        + str(link_rate) + ' '\
        + str(mean_link_delay) + ' '\
        + str(host_delay) + ' '\
        + str(load) + ' '\
        + str(connections_per_pair) + ' '\
        + str(mean_flow_size) + ' '\
        + str(flow_cdf) + ' '\
        + str(packet_size) + ' '\
        + str(queue_size) + ' '\
        + str(ecn_thresh) + ' '\
        + str(init_window) + ' '\
        + str(rto_min) + ' '\
        + str(dupack_thresh) + ' '\
        + str(enable_flowbender) + ' '\
        + str(flowbender_t) + ' '\
        + str(flowbender_n) + ' '\
        + str(fattree_k) + ' '\
        + str(topology_x) + ' '\
        + str('./' + directory_name + '/flow.tr') + '  >'\
        + str('./' + directory_name + '/log.tr')

    q.put([cmd, directory_name])


#Create all worker threads
threads = []
number_worker_threads = 20

#Start threads to process jobs
for i in range(number_worker_threads):
    t = threading.Thread(target = worker)
    threads.append(t)
    t.start()

#Join all completed threads
for t in threads:
    t.join()

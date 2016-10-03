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

flow_tot = 80000
link_rate = 1
mean_link_delay = 0.000001
host_delay = 0.000020
loads = [0.2, 0.4, 0.6, 0.8, 0.9]
connections_per_pair = 8
mean_flow_size = 1711250
flow_cdf = 'CDF_dctcp.tcl'
only_cross_rack = True

packet_size = 1460
switch_alg = 'DCTCP'
switch_queue_size = 300
switch_ecn_thresh = 20
nic_queue_size = 3333
nic_ecn_thresh = 3334

init_window = 10
rto_min = 0.010
dupack_thresh = 3
enable_flowbender = True
flowbender_t = 0.05
flowbender_n = 1

topology_spt = 6
topology_tors = 2
topology_spines = 4

ns_path = '/home/wei/load_balance/ns-allinone-2.35/ns-2.35/ns'
sim_script = 'spine_empirical.tcl'

special_str = 'spine_1g_'

for load in loads:
    scheme = 'ecmp'
    if enable_flowbender == True:
        scheme = 'flowbender'

    # directory name: websearch_[special str]_[LB scheme]_[load]
    directory_name = 'websearch_%s%s_%d' % (special_str, scheme, int(load * 100))
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
        + str(only_cross_rack) + ' '\
        + str(packet_size) + ' '\
        + str(switch_alg) + ' '\
        + str(switch_queue_size) + ' '\
        + str(switch_ecn_thresh) + ' '\
        + str(nic_queue_size) + ' '\
        + str(nic_ecn_thresh) + ' '\
        + str(init_window) + ' '\
        + str(rto_min) + ' '\
        + str(dupack_thresh) + ' '\
        + str(enable_flowbender) + ' '\
        + str(flowbender_t) + ' '\
        + str(flowbender_n) + ' '\
        + str(topology_spt) + ' '\
        + str(topology_tors) + ' '\
        + str(topology_spines) + ' '\
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

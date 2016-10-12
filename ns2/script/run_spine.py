import threading
import os
import Queue
import sys

####### flow size CDF file name -> workload name
def workload(file_name):
    if file_name == 'CDF_dctcp.tcl':
        return 'websearch'
    elif file_name == 'CDF_vl2.tcl':
        return 'datamining'
    elif file_name == 'CDF_fb.tcl':
        return 'facebook'
    else:
        return file_name.replace('CDF', '').replace('_', '').replace('tcl', '')

###### get mean flow size from the flow size CDF file
def get_mean_flow_size(file_name):
    f = open(file_name, 'rb')
    lines = f.readlines()
    f.close()

    cdf_array = []
    for line in lines:
        arr = line.split()
        if len(arr) == 3:
            cdf_array.append([int(arr[0]), float(arr[2])])

    if len(cdf_array) <= 1:
        return -1

    sum = 0.0
    for i in range(1, len(cdf_array)):
        sum = sum + (cdf_array[i][0] + cdf_array[i-1][0]) * (cdf_array[i][1] - cdf_array[i-1][1]) / 2
    return sum

###### create the directory (if not exist) and run simulation command
def worker():
    while True:
        try:
            j = q.get(block = 0)
        except Queue.Empty:
            return
        #Make directory to save results
        os.system('mkdir -p '+j[1])
        os.system(j[0])

q = Queue.Queue()

flow_tot = 50000
link_rate = 10
mean_link_delay = 0.000001
host_delay = 0.000020
loads = [0.2, 0.4, 0.6, 0.8, 0.9]
connections_per_pair = 10
flow_cdf = 'CDF_vl2.tcl'
mean_flow_size = get_mean_flow_size(flow_cdf)
only_cross_rack = True

packet_size = 1460
switch_alg = 'DCTCP'
switch_queue_size = 400
switch_ecn_thresh = 65
nic_queue_size = 400
nic_ecn_thresh = 65

source_alg = 'Agent/TCP/FullTcp/Newreno'
init_window = 10
rto_min = 0.010
dupack_thresh = 3
enable_flowbender = True
flowbender_t = 0.05
flowbender_n = 1

topology_spt = 8
topology_tors = 4
topology_spines = 4

ns_path = '/home/wei/load_balance/ns-allinone-2.35/ns-2.35/ns'
sim_script = 'spine_empirical.tcl'

special_str = 'spine_10g_'

if int(mean_flow_size) <= 0:
    print 'Invalid flow size CDF file %s' % flow_cdf
    sys.exit(0)

for load in loads:
    scheme = 'ecmp'
    if enable_flowbender == True:
        scheme = 'flowbender'

    # directory name: [workload]_[special str]_[LB scheme]_[load]
    directory_name = '%s_%s%s_%d' % (workload(flow_cdf), special_str, scheme, int(load * 100))
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
        + str(source_alg) + ' '\
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

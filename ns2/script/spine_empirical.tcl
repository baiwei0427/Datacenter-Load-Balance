source "tcp-traffic-gen.tcl"

set ns [new Simulator]

set flow_tot [lindex $argv 0]; #total number of flows to generate
set link_rate [lindex $argv 1]
set mean_link_delay [lindex $argv 2]
set host_delay [lindex $argv 3]
set load [lindex $argv 4]
set connections_per_pair [lindex $argv 5]
set mean_flow_size [lindex $argv 6]
set flow_cdf [lindex $argv 7]

#### Switch and NIC options
set packet_size [lindex $argv 8]
set switch_queue_size [lindex $argv 9]
set switch_ecn_thresh [lindex $argv 10]
set nic_queue_size [lindex $argv 11]
set nic_ecn_thresh [lindex $argv 12]

#### TCP options
set init_window [lindex $argv 13]
set rto_min [lindex $argv 14]
set dupack_thresh [lindex $argv 15]
set enable_flowbender [lindex $argv 16]
set flowbender_t [lindex $argv 17]
set flowbender_n [lindex $argv 18]

#### Topology
set topology_spt [lindex $argv 19]; #number of servers per ToR
set topology_tors [lindex $argv 20]; #number of ToR switches
set topology_spines [lindex $argv 21]; #number of spine (core) switches

### result file
set flowlog [open [lindex $argv 22] w]

set debug_mode 1
set sim_start [clock seconds]
set flow_gen 0; #the number of flows that have been generated
set flow_fin 0; #the number of flows that have finished
set source_alg Agent/TCP/FullTcp/Sack
set switch_alg RED

################## TCP #########################
Agent/TCP set ecn_ 1
Agent/TCP set old_ecn_ 1
Agent/TCP set dctcp_ true
Agent/TCP set dctcp_g_ 0.0625
Agent/TCP set windowInit_ $init_window
Agent/TCP set packetSize_ $packet_size
Agent/TCP set window_ 1000
Agent/TCP set slow_start_restart_ false
Agent/TCP set tcpTick_ 0.000001; # 1us should be enough
Agent/TCP set minrto_ $rto_min
Agent/TCP set rtxcur_init_ $rto_min; # initial RTO
Agent/TCP set maxrto_ 64
Agent/TCP set windowOption_ 0

Agent/TCP/FullTcp set tcprexmtthresh_ $dupack_thresh; #duplicate ACK threshold
Agent/TCP/FullTcp set nodelay_ true; # disable Nagle
Agent/TCP/FullTcp set segsize_ $packet_size
Agent/TCP/FullTcp set segsperack_ 1; # ACK frequency
Agent/TCP/FullTcp set interval_ 0.000006; #delayed ACK interval
Agent/TCP/FullTcp set flowbender_ $enable_flowbender
Agent/TCP/FullTcp set flowbender_t_ $flowbender_t
Agent/TCP/FullTcp set flowbender_n_ $flowbender_n

################ Queue #########################
Queue set limit_ $switch_queue_size
Queue/RED set bytes_ false
Queue/RED set queue_in_bytes_ true
Queue/RED set mean_pktsize_ [expr $packet_size + 40]
Queue/RED set setbit_ true
Queue/RED set gentle_ false
Queue/RED set q_weight_ 1.0
Queue/RED set mark_p_ 1.0
Queue/RED set thresh_ $switch_ecn_thresh
Queue/RED set maxthresh_ $switch_ecn_thresh

################ Multipathing ###########################
$ns rtproto DV
Agent/rtProto/DV set advertInterval [expr 2 * $flow_tot]
Node set multiPath_ 1
Classifier/MultiPath set perflow_ true
Classifier/MultiPath set debug_ false

######################## Topoplgy #########################
set topology_servers [expr $topology_spt * $topology_tors]; #number of servers
set topology_x [expr ($topology_spt + 0.0) / $topology_spines]

puts "$topology_servers servers in total, $topology_spt servers per rack"
puts "$topology_tors ToR switches"
puts "$topology_spines spine switches"
puts "Oversubscription ratio $topology_x"
flush stdout

for {set i 0} {$i < $topology_servers} {incr i} {
        set s($i) [$ns node]
}

for {set i 0} {$i < $topology_tors} {incr i} {
        set tor($i) [$ns node]
}

for {set i 0} {$i < $topology_spines} {incr i} {
        set spine($i) [$ns node]
}

############ Edge links ##############
for {set i 0} {$i < $topology_servers} {incr i} {
        set j [expr $i/$topology_spt]; # ToR ID
        $ns duplex-link $s($i) $tor($j) [set link_rate]Gb [expr $host_delay + $mean_link_delay] $switch_alg

        ####### Configure NIC queue
        set L [$ns link $s($i) $tor($j)]
        set q [$L set queue_]
        $q set limit_ $nic_queue_size
        $q set thresh_ $nic_ecn_thresh
        $q set maxthresh_ $nic_ecn_thresh
}

############ Core links ##############
for {set i 0} {$i < $topology_tors} {incr i} {
        for {set j 0} {$j < $topology_spines} {incr j} {
                $ns duplex-link $tor($i) $spine($j) [set link_rate]Gb $mean_link_delay $switch_alg
        }
}

#############  Agents ################
set lambda [expr ($link_rate * $load * 1000000000)/($topology_x * $mean_flow_size * 8.0 / $packet_size * ($packet_size + 40))]
puts "Core link average utilization: $load"
puts "Edge link average utilization: [expr $load / $topology_x]"
puts "Arrival: Poisson with inter-arrival [expr 1 / $lambda * 1000] ms"
puts "Average flow size: $mean_flow_size bytes"
puts "Setting up connections ..."; flush stdout

for {set j 0} {$j < $topology_servers} {incr j} {
        for {set i 0} {$i < $topology_servers} {incr i} {
                if {$j != $i} {
                        puts -nonewline "($i $j) "
                        set agtagr($i,$j) [new Agent_Aggr_pair]
                        $agtagr($i,$j) setup $s($i) $s($j) "$i $j" $connections_per_pair "TCP_pair" $source_alg
                        ## Note that RNG seed should not be zero
                        $agtagr($i,$j) set_PCarrival_process [expr $lambda / ($topology_servers - 1)] $flow_cdf [expr 17*$i+1244*$j] [expr 33*$i+4369*$j]
                        $agtagr($i,$j) attach-logfile $flowlog

                        $ns at 0.1 "$agtagr($i,$j) warmup 0.5 $packet_size"
                        $ns at 1 "$agtagr($i,$j) init_schedule"
                }
        }
        puts ""
        flush stdout
}

puts "Initial agent creation done"
puts "Simulation started!"
$ns run

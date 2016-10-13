set ns [new Simulator]

set rtt 0.000080
set link_rate 10
set packet_size 1460
set rto_min 0.005
set flow_size 50000
set num_flow 5
set switch_alg DCTCP
set queue_size 333
set ecn_thresh 65

################## TCP #########################
Agent/TCP set ecn_ 1
Agent/TCP set old_ecn_ 1
Agent/TCP set dctcp_ true
Agent/TCP set dctcp_g_ 0.0625
Agent/TCP set windowInit_ 10
Agent/TCP set packetSize_ $packet_size
Agent/TCP set window_ 1256
Agent/TCP set slow_start_restart_ false
Agent/TCP set tcpTick_ 0.000001; # 1us should be enough
Agent/TCP set minrto_ $rto_min
Agent/TCP set rtxcur_init_ $rto_min; # initial RTO
Agent/TCP set maxrto_ 64
Agent/TCP set windowOption_ 0

Agent/TCP/FullTcp set nodelay_ true; # disable Nagle
Agent/TCP/FullTcp set segsize_ $packet_size
Agent/TCP/FullTcp set segsperack_ 1; # ACK frequency
Agent/TCP/FullTcp set interval_ 0.000006; #delayed ACK interval
Agent/TCP/FullTcp set flowbender_ false
Agent/TCP/FullTcp set flowbender_t_ 0.05
Agent/TCP/FullTcp set flowbender_n_ 1
Agent/TCP/FullTcp set restart_ true

################ Queue #########################
Queue set limit_ $queue_size
Queue/DCTCP set mean_pktsize_ [expr $packet_size + 40]
Queue/DCTCP set thresh_ $ecn_thresh

################ Topology #####################
set n0 [$ns node]
set n1 [$ns node]
$ns duplex-link $n0 $n1 [set link_rate]Gb [expr $rtt / 2] $switch_alg

set tcps [new Agent/TCP/FullTcp/Sack]
set tcpr [new Agent/TCP/FullTcp/Sack]
$ns attach-agent $n0 $tcps
$ns attach-agent $n1 $tcpr
$tcpr listen
$ns connect $tcps $tcpr

##### The function is called when the flow finishes ######3
Agent/TCP/FullTcp instproc done_data {} {
        global ns start_time tcps flow_size num_flow flow_fin

        set fct [expr [$ns now] - $start_time]
        set cwnd [$tcps set cwnd_]
        incr flow_fin
        puts "($flow_fin) FCT: $fct Cwnd: $cwnd"
        set start_time [$ns now]

        if {$flow_fin == $num_flow} {
                $ns at $start_time "finish"
        } else {
                $tcps set signal_on_empty_ TRUE
                $ns at $start_time "$tcps advance-bytes $flow_size"
        }
}

proc finish {} {
        exit 0
}

$tcps set signal_on_empty_ TRUE; # call done_data() when the flow finishes
set start_time [$ns now]
set flow_fin 0
$ns at [expr 0.0] "$tcps advance-bytes $flow_size"
$ns run

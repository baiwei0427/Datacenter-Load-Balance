#ifndef ns_my_red_h
#define ns_my_red_h

#include "queue.h"

/* MyRED: a simple version of Random Early Detection (RED) for DCTCP-style ECN marking */
class MyRED : public Queue
{
public:
        MyRED();
        ~MyRED();

protected:
        void enque(Packet*);
	Packet* deque();
        virtual int command(int argc, const char*const* argv);
	void trace_qlen();     /* routine to write qlen records */

        PacketQueue *q_;        /* underlying (usually) FIFO queue */

        int thresh_;    /* ECN marking threshold in packet */
        int mean_pktsize_;      /* packet size in bytes */
        int pkt_total_; /* total number of packets */
        int pkt_mark_;  /* total number of packets marked */
        int pkt_drop_;  /* total number of packets dropped by the port */

        Tcl_Channel qlen_tchan_;        /* place to write queue length records */
};

#endif

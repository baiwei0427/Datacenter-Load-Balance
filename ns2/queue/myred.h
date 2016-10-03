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

        int thresh_;    /* ECN marking threshold in packet */
        int mean_pktsize_;      /* packet size in bytes */
        int pkt_total_; /* total number of packets */
        int pkt_drop_;  /* total number of packets dropped by the port */

        PacketQueue *q_;        /* underlying (usually) FIFO queue */
};

#endif

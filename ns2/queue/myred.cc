#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "flags.h"
#include "myred.h"

#ifndef max
    #define max(a,b) ((a) > (b) ? (a) : (b))
#endif

static class MyREDClass : public TclClass
{
	public:
		MyREDClass():TclClass("Queue/DCTCP") {}
		TclObject* create(int argc, const char*const* argv)
		{
			return (new MyRED);
		}
} class_myred;

MyRED::MyRED()
{
	q_ = new PacketQueue();

	thresh_ = 65;
	mean_pktsize_ = 1500;
        pkt_total_ = 0;
        pkt_mark_ = 0;
	pkt_drop_ = 0;

        qlen_tchan_ = NULL;

	bind("thresh_", &thresh_);
	bind("mean_pktsize_", &mean_pktsize_);
	bind("pkt_total_", &pkt_total_);
        bind("pkt_mark_", &pkt_mark_);
	bind("pkt_drop_", &pkt_drop_);
}

MyRED::~MyRED()
{
	delete q_;
}

void MyRED::enque(Packet* p)
{
        hdr_flags* hf = hdr_flags::access(p);
        int len = hdr_cmn::access(p)->size() + q_->byteLength();
        pkt_total_++;

        if (len > qlim_ * mean_pktsize_)
        {
                drop(p);
                pkt_drop_++;
                return;
        }

        if (len > thresh_ * mean_pktsize_ && hf->ect())
        {
                hf->ce() = 1;
                pkt_mark_++;
        }

        q_->enque(p);
}

Packet* MyRED::deque()
{
        trace_qlen();
        return q_->deque();
}

/*
 * $q trace-qlen file
 */
int MyRED::command(int argc, const char*const* argv)
{
        if (argc == 3)
        {
                if (strcmp(argv[1], "trace-qlen") == 0)
                {
                        int mode;
                        const char* id = argv[2];
                        Tcl& tcl = Tcl::instance();
                        if ((qlen_tchan_ = Tcl_GetChannel(tcl.interp(), (char*)id, &mode)) == 0)
                        {
                                tcl.resultf("DCTCP: trace: can't attach %s for writing", id);
        			return (TCL_ERROR);
        		}

                        return (TCL_OK);
                }
        }

        return (Queue::command(argc, argv));
}

/* routine to write queue length records */
void MyRED::trace_qlen()
{
        if (!qlen_tchan_ || !q_)
                return;

        char wrk[100];
        memset(wrk, 0, 100);
        sprintf(wrk, "%g , %d\n", Scheduler::instance().clock(), q_->byteLength());
        Tcl_Write(qlen_tchan_, wrk, strlen(wrk));
}

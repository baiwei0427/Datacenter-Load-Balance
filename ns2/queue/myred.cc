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
	pkt_drop_ = 0;

	bind("thresh_", &thresh_);
	bind("mean_pktsize_", &mean_pktsize_);
	bind("pkt_total_", &pkt_total_);
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
                hf->ect() = 1;
        }

        q_->enque(p);
}

Packet* MyRED::deque()
{
        return q_->deque();
}

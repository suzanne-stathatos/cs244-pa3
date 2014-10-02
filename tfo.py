#!/usr/bin/python

"CS244 Assignment 3: TCP Fast Open Implementation"

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

import subprocess
from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
import termcolor as T
from argparse import ArgumentParser

import ftplib
import socket
import sys
import os
from util.monitor import monitor_qlen
from util.helper import stdev

def cprint(s, color, cr=True):
    """Print in color
       s: string to print
       color: color to use"""
    if cr:
        print T.colored(s, color)
    else:
        print T.colored(s, color),


# Parse arguments

parser = ArgumentParser(description="Buffer sizing tests")
parser.add_argument('--bw-host', '-B',
                    dest="bw_host",
                    type=float,
                    action="store",
                    help="Bandwidth of host links",
                    required=True)

parser.add_argument('--bw-net', '-b',
                    dest="bw_net",
                    type=float,
                    action="store",
                    help="Bandwidth of network link",
                    required=True)

parser.add_argument('--delay',
                    dest="delay",
                    type=float,
                    help="Delay in milliseconds of host links",
                    default=87)

parser.add_argument('--page', '-p',
		   dest="page",
		   action="store",
		   help="Name of webpage to fetch",
		   required=True)

parser.add_argument('--dir', '-d',
                    dest="dir",
                    action="store",
                    help="Directory to store outputs",
                    default="results",
                    required=False)

parser.add_argument('-n',
                    dest="n",
                    type=int,
                    action="store",
                    help="Number of nodes in star.  Must be >= 3",
                    required=False)

parser.add_argument('--maxq',
                    dest="maxq",
                    action="store",
                    help="Max buffer size of network interface in packets",
                    default=1000)

parser.add_argument('--cong',
                    dest="cong",
                    help="Congestion control algorithm to use",
                    default="bic")


parser.add_argument('--iperf',
                    dest="iperf",
                    help="Path to custom iperf",
                    required=False)

parser.add_argument('--tfo',
		   dest="tfo",
		   action='store_true',
		   help="TFO enabled",
	  	   required=False)

# Expt parameters
args = parser.parse_args()

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')

# Topology to be instantiated in Mininet
class StarTopo(Topo):
    "Star topology for TCP Fast Open experiment"

    def __init__(self, n=3, cpu=None, bw_host=None, bw_net=None,
                 delay=None, maxq=None, tfo=False, page=None):
        # Add default members to class.
        super(StarTopo, self ).__init__()
        self.n = n
        self.cpu = cpu
        self.bw_host = bw_host
        self.bw_net = bw_net
        self.delay = delay
        self.page = page
	self.maxq = maxq
        self.tfo = tfo
	self.create_topology()
	
    def create_topology(self):
	# set up switch
	s0 = self.addSwitch('s0')

	# set up pseudo-server from which to download pages
	h0 = self.addHost('h0')

	# set up host to download pages
	h1 = self.addHost('h1')

	# flows
	self.addLink(h0, s0, delay=self.delay, bw=self.bw_net, max_queue_size = self.maxq)
	self.addLink(h1, s0, delay=self.delay, bw=self.bw_net, max_queue_size = self.maxq)

def verify_latency(net):
    cprint('verifying latency...', 'yellow') 
    # check latency from each stanford host to rice
    h0 = net.getNodeByName('h0')
    h1 = net.getNodeByName('h1')
    ping = h1.cmd('ping -c 5 -q ' + str(h0.IP()))
    print ping
    cprint('latency verified', 'green')    

def start_webserver(net):
    h0 = net.getNodeByName('h0')
    proc = h0.popen("sudo python http/webserver.py", shell=True)
    sleep(1)
    return [proc]

def fetch_webpage(net):
    h0 = net.getNodeByName('h0')
    h1 = net.getNodeByName('h1')
    start = time()
    url = "%s/pages/%s" %(h0.IP(), args.page)
    cmd = '/usr/bin/time -f "%e"'
    start = time()
    mget_time = h1.cmd("%s %s -r -p --no-http-keep-alive --no-cache --delete-after --directories=off %s > %s" %(cmd, 'mget', url, '/dev/null'))
    end = time()
    total = end-start
    return total

def start_receiver(net):
    h1 = net.getNodeByName('h1')
    print "Starting iperf receiver..."
    receiver = h1.popen('%s -s -p %s > %s/iperf_server.txt' % (CUSTOM_IPERF_PATH, 5001, args.dir), shell=True)

def start_senders(net):
    print "Starting iperf senders..."
    # Seconds to run iperf; keep this very high
    seconds = 3600
    server = net.getNodeByName('h0')    
    output_file = 'output'
    sender = net.getNodeByName('h1')
    sender.popen('%s -c %s -p %s -t %d -i 1 -yc -Z %s > %s%s' % (CUSTOM_IPERF_PATH, server.IP(), 5001, seconds, args.cong, args.dir, output_file), shell=True)

def main():
    "Create network and run TFO experiment"

    start = time()
    # Reset to known state
    topo = StarTopo(n=args.n, bw_host=args.bw_host,
                    delay='%sms' % args.delay,
                    bw_net=args.bw_net, tfo=args.tfo, 
		    maxq=args.maxq, page=args.page)
    
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()

    #verify_latency(net)
    #start_receiver(net)

    cprint("Starting experiment", "yellow")
    #start_senders(net)
    start_webserver(net)
    #CLI(net)
    with open('/dev/null', 'w+') as out:
    	Popen("rm -r ./cache", shell=True, stdout=out, stderr=out).wait()
    	timeX = fetch_webpage(net)
    	cprint("Got " + args.page + " for RTT of " + str(round(4*args.delay, 0)) + " in " + str(round(timeX, 2)) + "sec", "green")
	Popen("rm -r ./cache", shell=True, stdout=out, stderr=out).wait()

    	# Store output.  It will be parsed by run.sh after the entire
    	# sweep is completed.  Do not change this filename!
   
    if (args.tfo):
	tfo = "TFO"
    else:
	tfo = "Non-TFO"
    output = "%s\t %s \t %s \t %s \n" % (args.page, tfo, 4*args.delay, round(timeX,2))
    folder = "%s/tfo-%s/" %(args.dir, args.tfo)
   
    #CLI(net)
    if not os.path.exists(folder):
      os.makedirs(folder)
    open("%s/result.txt" %(folder), "a").write(output)


    net.stop()
    Popen("killall -9 top bwm-ng mnexec", shell=True).wait()
    end = time()

if __name__ == '__main__':
    try:
        main()
    except:
        print "-"*80
        print "Caught exception.  Cleaning up..."
        print "-"*80
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng cat mnexec iperf; mn -c")


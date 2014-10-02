#!/bin/bash

# USE FOR TFO RUN

# Exit on any failure
set -e

# Check for uninitialized variables
set -o nounset

ctrlc() {
	killall -9 python
	mn -c
	exit
}

trap ctrlc SIGINT

start=`date`
exptid=`date +%b%d-%H:%M`

rootdir=tfo-$exptid
plotpath=util
iperf=~/iperf-patched/src/iperf

# Links are numbered as switchname-eth1,2,etc in the order they are
# added to the topology.
iface=s0-eth1


for page in 'amazon' 'nytimes' 'wsj' 'wiki'; do
  for max_RTT in 5 25 50; do #NOTE: these are 20, 100, 200 divided across 4 links
	dir=$rootdir/$page
	echo 'RTT/4: ' $max_RTT
	echo 'page: '  $page
	echo 'dir: ' $dir
	python tfo.py --bw-host 4 \
		--bw-net 4 \
		--delay $max_RTT \
		--dir $dir \
		--page $page \
		--tfo\
		-n 3 \
		--iperf $iperf
  done
done

echo 'page     TFO   RTT    PLT'
cat $rootdir/*/*/result.txt

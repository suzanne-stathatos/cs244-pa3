cs244-pa3
=========

TCP Fast Open Replication

Project done with Laura Garrity (https://github.com/lgarrity)

1. Create two t1.micro instances, one for TFO and one for non-TFO.
For TFO: use AMI cs244-tfo-sg in US-West (Oregon) / AMI ID ami-3f4f3c0f
For non-TFO: use AMI cs244-no-tfo-sg in US-West (Oregon) / AMI ID ami-a54e3d95

2. Fire up both instances (username: ubuntu) and clone the git repository: 
git clone https://github.com/lgarrity/cs244-pa3

3. Change into the cs244-pa3 directory and run the script.
For the TFO instance, type sudo ./run-tfo.sh
For the non-TFO instance, type sudo ./run-no-tfo.sh

The results for each will print out at the end of the run (each run lasts approximately 5 minutes).

NB: If you need to stop in the middle, ensure you cleanup Mininet before running again (sudo mn -c).

NB: If you are trying to reproduce without the AMI, you’ll need to ensure that you have the following installed:
- Ubuntu 14.04
- Linux kernel 3.14
- mget (with dependencies) (available here: https://github.com/rockdaboot/mget


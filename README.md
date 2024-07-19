# lab_automation
Repo containing software used for automation of various lab resources.

# Secondary DNS functionality
### Secondary DNS implementation with dnsmasq

Instructions (Please refer below commands in bold to perform #2,3,4) -
1. Prepare the Dockerfile, dnsmasq.conf, and add_hosts_entries.sh files, ensuring they are all in one directory.
2. Build the Docker image using the 'docker build' command.
3. Run the Docker container using the 'docker run' custom command with the necessary port mappings to update the hosts file and start dnsmasq.
4. Access the container using 'docker exec' to run 'nslookup' commands to check secondary DNS functionality.
5. To add your own entry in the /etc/hosts file, please add it in the add_hosts_entries.sh script with this syntax: 'IP X.noiro.lab X'.

Summary - With these steps, we have dnsmasq running in a Docker container, configured to listen on port 53, and our specified hosts entries added.

### Workflow and Configuration Samples

Listed below are some examples (in nslookup interactive mode as desired) to show the functionality/workflow.

A. **docker build -t my-dnsmasq-image-z108 .**

B. **docker run -d --name my-dnsmasq-container-z108 -p 5355:53/udp my-dnsmasq-image-z108 /bin/sh -c "/usr/local/bin/add_hosts_entries.sh && dnsmasq -k"**

```
vlella@VLELLA-M-F9W9 etc % sudo lsof -i :5355
COMMAND     PID   USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
com.docke 55277 vlella  136u  IPv6 0xcf06771614417068      0t0  UDP *:llmnr
```

```
vlella@VLELLA-M-F9W9 etc % nslookup -port=5355    
> server 127.0.0.1
Default server: 127.0.0.1
Address: 127.0.0.1#5355
> ff00::0
Server:                    127.0.0.1
Address:  127.0.0.1#5355
 
0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.f.f.ip6.arpa    name = ip6-mcastprefix.
> 172.17.0.2
Server:                    127.0.0.1
Address:  127.0.0.1#5355
 
2.0.17.172.in-addr.arpa           name = a13ecb9392b2.
> a13ecb9392b2
Server:                    127.0.0.1
Address:  127.0.0.1#5355
 
Name:     a13ecb9392b2
Address: 172.17.0.2
> ff02::2
Server:                    127.0.0.1
Address:  127.0.0.1#5355
 
2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.2.0.f.f.ip6.arpa    name = ip6-allrouters.
```

C. Inside ubuntu container -

vlella@VLELLA-M-F9W9 etc % **sudo docker exec -it my-dnsmasq-container-z108 /bin/sh**

```
# cat /etc/hosts
127.0.0.1   localhost
::1            localhost ip6-localhost ip6-loopback
fe00::0      ip6-localnet
ff00::0      ip6-mcastprefix
ff02::1      ip6-allnodes
ff02::2      ip6-allrouters
172.17.0.2 a13ecb9392b2
172.28.184.20   f1-apic-1.noiro.lab f1-apic-1
172.28.184.26   f1-compute-1.noiro.lab f1-compute-1
172.28.184.27   f1-compute-2.noiro.lab f1-compute-2
172.28.184.25   f1-controller.noiro.lab f1-controller
172.28.184.21   f1-leaf-1.noiro.lab f1-leaf-1
172.28.184.22   f1-leaf-2.noiro.lab f1-leaf-2
172.28.184.23   f1-spine-1.noiro.lab f1-spine-1
172.28.184.30   f2-apic-1.noiro.lab f2-apic-1
172.28.184.36   f2-compute-1.noiro.lab f2-compute-1
172.28.184.37   f2-compute-2.noiro.lab f2-compute-2
172.28.184.35   f2-controller.noiro.lab f2-controller
172.28.184.31   f2-leaf-1.noiro.lab f2-leaf-1
172.28.184.32   f2-leaf-2.noiro.lab f2-leaf-2
172.28.184.33   f2-spine-1.noiro.lab f2-spine-1
172.28.184.40   f3-apic-1.noiro.lab f3-apic-1
172.28.184.46   f3-compute-1.noiro.lab f3-compute-1
172.28.184.47   f3-compute-2.noiro.lab f3-compute-2
172.28.184.45   f3-controller.noiro.lab f3-controller
172.28.184.41   f3-leaf-1.noiro.lab f3-leaf-1
172.28.184.42   f3-leaf-2.noiro.lab f3-leaf-2
172.28.184.43   f3-spine-1.noiro.lab f3-spine-1
172.28.184.80   f4-apic-1.noiro.lab f4-apic-1
172.28.184.83   f4-compute-1.noiro.lab f4-compute-1
172.28.184.84   f4-compute-2.noiro.lab f4-compute-2
172.28.184.82   f4-controller.noiro.lab f4-controller
172.28.184.81   f4-leaf-1.noiro.lab f4-leaf-1
172.28.184.60   f5-apic-1.noiro.lab f5-apic-1
172.28.184.63   f5-compute-1.noiro.lab f5-compute-1
172.28.184.64   f5-compute-2.noiro.lab f5-compute-2
172.28.184.65   f5-controller.noiro.lab f5-controller
172.28.184.61   f5-leaf-1.noiro.lab f5-leaf-1
10.30.120.151   fab10-compute-1.noiro.lab fab10-compute-1
10.30.120.152   fab10-compute-2.noiro.lab fab10-compute-2
10.30.120.153   fab10-compute-3.noiro.lab fab10-compute-3
10.30.120.154   fab10-compute-4.noiro.lab fab10-compute-4
10.30.120.155   fab10-compute-5.noiro.lab fab10-compute-5
10.30.120.185   fab11-compute-1.noiro.lab fab11-compute-1
10.30.120.186   fab11-compute-2.noiro.lab fab11-compute-2
10.30.120.95    fab6-compute-1.noiro.lab fab6-compute-1
10.30.120.96    fab6-compute-2.noiro.lab fab6-compute-2
10.30.120.97    fab6-controller.noiro.lab fab6-controller
10.30.120.105   fab7-compute-1.noiro.lab fab7-compute-1
10.30.120.106   fab7-compute-2.noiro.lab fab7-compute-2
10.30.120.107   fab7-controller.noiro.lab fab7-controller
10.30.120.115   fab8-compute-1.noiro.lab fab8-compute-1
10.30.120.116   fab8-compute-2.noiro.lab fab8-compute-2
10.30.120.117   fab8-controller.noiro.lab fab8-controller
10.30.120.186   hypf-vc65.noiro.lab hypf-vc65
172.28.184.8    noiro-ctrl-srvr.noiro.lab noiro-ctrl-srvr
172.28.184.18   noiro-dns.noiro.lab noiro-dns
10.30.120.16    noiro-hyper-4.noiro.lab noiro-hyper-4
10.30.120.17    noiro-hyper-5.noiro.lab noiro-hyper-5
10.30.120.18    noiro-hyper-6.noiro.lab noiro-hyper-6
10.30.120.19    noiro-hyper-7.noiro.lab noiro-hyper-7
10.30.120.21    noiro-hyper-8.noiro.lab noiro-hyper-8
10.30.120.11    noiro-infra-1.noiro.lab noiro-infra-1
10.30.120.12    noiro-infra-2.noiro.lab noiro-infra-2
10.30.120.13    noiro-infra-3.noiro.lab noiro-infra-3
172.28.184.9    noiro-jenkins.noiro.lab noiro-jenkins
10.30.120.7     noiro-nfs.noiro.lab noiro-nfs
172.28.184.200  noiro-rack-1-dist.noiro.lab noiro-rack-1-dist
172.28.184.201  noiro-rack-2-dist.noiro.lab noiro-rack-2-dist
172.28.184.202  noiro-rack-3-dist.noiro.lab noiro-rack-3-dist
172.28.184.203  noiro-rack-4-dist.noiro.lab noiro-rack-4-dist
172.28.184.204  noiro-rack-5-dist.noiro.lab noiro-rack-5-dist
172.28.184.205  noiro-rack-6-dist.noiro.lab noiro-rack-6-dist
172.28.184.206  noiro-rack-7-dist.noiro.lab noiro-rack-7-dist
172.28.184.14   noiro-rh-mirror.noiro.lab noiro-rh-mirror
172.28.184.114  opflex-pt-1.noiro.lab opflex-pt-1
10.30.120.194   ostack-pt-1.noiro.lab ostack-pt-1
10.30.120.14    ovirt-engine.noiro.lab ovirt-engine
10.30.120.31    sg1-compute-1.noiro.lab sg1-compute-1
10.30.120.40    sg1-compute-10.noiro.lab sg1-compute-10
10.30.120.41    sg1-compute-11.noiro.lab sg1-compute-11
10.30.120.42    sg1-compute-12.noiro.lab sg1-compute-12
10.30.120.43    sg1-compute-13.noiro.lab sg1-compute-13
10.30.120.44    sg1-compute-14.noiro.lab sg1-compute-14
10.30.120.45    sg1-compute-15.noiro.lab sg1-compute-15
10.30.120.46    sg1-compute-16.noiro.lab sg1-compute-16
10.30.120.32    sg1-compute-2.noiro.lab sg1-compute-2
10.30.120.33    sg1-compute-3.noiro.lab sg1-compute-3
10.30.120.34    sg1-compute-4.noiro.lab sg1-compute-4
10.30.120.35    sg1-compute-5.noiro.lab sg1-compute-5
10.30.120.36    sg1-compute-6.noiro.lab sg1-compute-6
10.30.120.37    sg1-compute-7.noiro.lab sg1-compute-7
10.30.120.38    sg1-compute-8.noiro.lab sg1-compute-8
10.30.120.39    sg1-compute-9.noiro.lab sg1-compute-9
172.28.184.7    termserv.noiro.lab termserv
192.168.23.11   robin1.noiro.lab robin1
192.168.23.12   robin2.noiro.lab robin2
192.168.23.13   robin3.noiro.lab robin3
192.168.23.14   robin4.noiro.lab robin4
192.168.23.16   robin5.noiro.lab robin5
#
```

```
# nslookup -port=53
> server 127.0.0.1
Default server: 127.0.0.1
Address: 127.0.0.1#53
> f5-controller.noiro.lab
Server:                    127.0.0.1
Address:  127.0.0.1#53
 
Name:     f5-controller.noiro.lab
Address: 172.28.184.65
> fab8-controller
Server:                    127.0.0.1
Address:  127.0.0.1#53
 
Name:     fab8-controller
Address: 10.30.120.117
> 192.168.23.16
16.23.168.192.in-addr.arpa     name = robin5.noiro.lab.
> 172.28.184.65
65.184.28.172.in-addr.arpa     name = f5-controller.noiro.lab.
> 10.30.120.186
186.120.30.10.in-addr.arpa     name = fab11-compute-2.noiro.lab.
> ip6-allnodes
Server:                    127.0.0.1
Address:  127.0.0.1#53
 
Name:     ip6-allnodes
Address: ff02::1
> broadcasthost
Server:                    127.0.0.1
Address:  127.0.0.1#53
 
Non-authoritative answer:
Name:     broadcasthost
Address: 255.255.255.255
> noiro-nfs
Server:                    127.0.0.1
Address:  127.0.0.1#53
 
Name:     noiro-nfs
Address: 10.30.120.7
> fe00::0
0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.e.f.ip6.arpa    name = ip6-localnet.
```

D. Once you stop the container then you see on the host port 5355 doesn't function anymore -
```
vlella@VLELLA-M-F9W9 etc % docker stop my-dnsmasq-container-z108
my-dnsmasq-container-z108
vlella@VLELLA-M-F9W9 etc % nslookup -port=5355                 
> server 127.0.0.1
Default server: 127.0.0.1
Address: 127.0.0.1#5355
> ff00::0
;; connection timed out; no servers could be reached
> f4-compute-2.noiro.lab
;; connection timed out; no servers could be reached
>
```

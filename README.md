# Host Identity Based VPLS tailored for NanoPiR2S

Deployment scenario:

+---------+ 100Mb/s  +-----------+ 100Mb/s+----------------+

| IP cam  |----------| CE Switch |--------| Ambient sensors|
+---------+          +-----------+        +----------------+
                            |
                            | 1 Gb/s
                            |
                     +-----------+
                     |HIP switch |
                     +-----------+
                            |                                                 +------------------+
                            | 1 Gb/s                                          | Sensors/Actuators|
                            |                                                /+------------------+
+-----------+  1Gb/s +--------------+1 Gb/s+-----------+ 1 Gb/s+-----------+/ 100 Mb/s
|HIP switch |--------| Public cloud |------|HIP switch |-------| CE Switch |
+-----------+        +--------------+      +-----------+       +-----------+
                            |  |                                            \ 100 Mb/s
                            |  +--------+                                    \
                            | 1 Gb/s    |                                     +------------------+
                       +-----------+    |                                     | Sensors/Actuators|
                       |HIP switch |    |                                     +------------------+
                       +-----------+    |
                            | 1 Gb/s    |
+-----------+ 1 Gb/s   +-----------+    | 10 Mb/s
|  Server   |----------|CE switch  |    |
+-----------+     +----+-----------+    |
                  |          | 1 Gb/s   |
+-----------+-----+          |          |
| DHCP/DNS  | 1 Gb/s   +-----------+    |
+-----------+          |   Router  |----+
                       +-----------+
                       

To deploy HIP-VPLS on hardware (HIP switch) follow these steps:

In folder hip-vpls-hw edit the following files:
- hosts (Add mapping between HIT and IP address)
- mesh (add all pairs of HITs)
- config.py (change the CE facing interface, public source IP address)

Next deploy the service:

```
$ git clone git@github.com:strangebit-io/hip-vpls-hw.git
$ cd hip-vpls-hw
$ cd deploy
$ sudo bash deploy.sh
```

Finally run the service:
```
$ sudo service hip-vpls start
```

Repeat the same procedure on all HIP switches.

# Stress test scenarios

We have tested the testbed in the following way:
- end-to-end iperf test
- multicast traffic (RTSP stream to a multicast source)

# Compiling the source code for performance

To be done


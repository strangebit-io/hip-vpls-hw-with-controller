#!/usr/bin/python3

# Copyright (C) 2022 strangebit

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Dmitriy Kuptsov"
__copyright__ = "Copyright 2022, stangebit"
__license__ = "GPL"
__version__ = "0.0.1b"
__maintainer__ = "Dmitriy Kuptsov"
__email__ = "dmitriy.kuptsov@gmail.com"
__status__ = "development"

# Import the needed libraries
# OS library
import os
# Stacktrace
import traceback
# Sockets
import socket
# Threading
import threading
# Logging
import logging
# Timing
import time
# Math functions
from math import ceil, floor
# System
import sys
# Exit handler
import atexit
# Timing 
from time import sleep
from time import time

# Hex
from binascii import hexlify

# Import HIP library
from hiplib import hlib

# Utilities
from hiplib.utils import misc

# Crypto stuff
from hiplib.crypto import digest

from hiplib.hlib import HIPLib

# HIP related packets
from hiplib.packets import HIP
# IPSec packets
from hiplib.packets import IPSec
# IPv6 packets
from hiplib.packets import IPv6
# IPv4 packets 
from hiplib.packets import IPv4
# Ethernet frame
from hiplib.packets import Ethernet
# Controller packets
from hiplib.packets import Controller
# Configuration
from hiplib.config import config as hip_config
# Import switch FIB
from switchfabric import FIB

# Network stuff
import socket
import ssl

# HIP controller lock
hip_config_socket_lock = threading.Lock()

# Copy routines
import copy

# Configure logging to console and file
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        #logging.FileHandler("hipls.log")#,
        logging.StreamHandler(sys.stdout)
    ]
);

# HIP configuration 
hiplib = HIPLib(hip_config.config);

hip_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, HIP.HIP_PROTOCOL);
hip_socket.bind(("0.0.0.0", HIP.HIP_PROTOCOL));
# We will need to perform manual fragmentation
hip_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1);
logging.info("Initializing IPSec socket");
ip_sec_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, IPSec.IPSEC_PROTOCOL);
#ip_sec_socket.bind(("0.0.0.0", IPSec.IPSEC_PROTOCOL));
ip_sec_socket.bind((hip_config.config["swtich"]["source_ip"], IPSec.IPSEC_PROTOCOL))

# We will need to perform manual fragmentation
ip_sec_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1);
# Open raw ethernet socket and bind it to the interface
ETH_P_ALL = 3
ether_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL));
ether_socket.bind((hip_config.config["swtich"]["l2interface"], 0))

# Initialize FIB
fib = FIB(hip_config.config["swtich"]["mesh"])

hip_config_socket = None

def onclose():
    packets = hiplib.exit_handler()
    for (packet, dest) in packets:
        hip_socket.sendto(packet, dest)

def open_controller_socket():
    """
    Conncects to controller in the cloud
    """
    ctx = ssl.create_default_context();
    ctx.load_verify_locations(hip_config.config["controller"]["ca_cert"]);
    ip = socket.gethostbyname(hip_config.config["controller"]["controller_host_name"])
    sock = socket.create_connection((ip, hip_config.config["controller"]["controller_port"]));
    ctx.check_hostname = True;
    secure_socket = ctx.wrap_socket(sock, server_hostname=hip_config.config["controller"]["controller_host_name"], 
                                    server_side=False);
    return secure_socket

def write_rules_to_file(rules):
    fd = open(hip_config.config["firewall"]["rules_file"], "w")
    for rule in rules:
        hit1 = misc.Utils.ipv6_bytes_to_hex_formatted_resolver(rule["hit1"])
        hit2 = misc.Utils.ipv6_bytes_to_hex_formatted_resolver(rule["hit2"])
        if rule["rule"] == 1:
            rule = "allow"
        else:
            rule = "deny"
        fd.write(hit1 + " " + hit2 + " " + rule + "\n")
    fd.close();
    hiplib.firewall.load_rules(hip_config.config["firewall"]["rules_file"])

def write_mesh_to_file(mesh):
    fd = open(hip_config.config["swtich"]["mesh"], "w")
    for m in mesh:
        hit1 = misc.Utils.ipv6_bytes_to_hex_formatted_resolver(mesh["hit1"])
        hit2 = misc.Utils.ipv6_bytes_to_hex_formatted_resolver(mesh["hit2"])
        fd.write(hit1 + " " + hit2 + "\n")
    fd.close();
    fib.load_mesh(hip_config.config["switch"]["mesh"])

def write_hosts_to_file(hosts):
    fd = open(hip_config.config["resolver"]["hosts_file"], "w")
    for host in hosts:
        hit = misc.Utils.ipv6_bytes_to_hex_formatted_resolver(host["hit"])
        ip = misc.Utils.ipv4_bytes_to_string(host["ip"])
        fd.write(hit + " " + ip + "\n")
    fd.close();
    hiplib.hit_resolver.load_records(hip_config.config["resolver"]["hosts_file"])

def config_loop():
    try:
        hip_config_socket_lock.acquire();
        if not hip_config_socket:
            hip_config_socket = open_controller_socket();
    finally:
        hip_config_socket_lock.release();
    buf = bytearray([])
    while True:
        buf += bytearray(hip_config_socket.recv(hip_config.config["default_buffer"]["default_buffer"]))
        while len(buf) >= Controller.BASIC_HEADER_OFFSET:
            packet = Controller.ControllerPacket(buf)
            if packet.get_packet_length() > len(buf):
                break
            pbuf = buf[:packet.get_packet_type()]
            buf = buf[packet.get_packet_type():]
            
            if packet.get_packet_type() == Controller.FIREWALL_CONFIGURATION_TYPE:
                packet = Controller.FirewallConfigurationPacket(pbuf)
                hmac = packet.get_hmac()
                packet.set_hmac([0]*digest.SHA256Digest.LENGTH)
                hmac = digest.SHA256HMAC(hip_config.config["controller"]["master_secret"])            
                if hmac != hmac.digest(packet.get_buffer()):
                    logging.critical("Invalid HMAC in the packet")
                rules = packet.get_rules()
                write_rules_to_file(rules)
            elif packet.get_packet_type() == Controller.MESH_CONFIGURATION_TYPE:
                packet = Controller.MeshConfigurationPacket(pbuf)
                hmac = packet.get_hmac()
                packet.set_hmac([0]*digest.SHA256Digest.LENGTH)
                hmac = digest.SHA256HMAC(hip_config.config["controller"]["master_secret"])            
                if hmac != hmac.digest(packet.get_buffer()):
                    logging.critical("Invalid HMAC in the packet")
                mesh = packet.get_mesh();
                write_mesh_to_file(mesh)
            elif packet.get_packet_type() == Controller.HOSTS_CONFIGURATION_TYPE:
                packet = Controller.HostsConfigurationPacket(pbuf)
                hmac = packet.get_hmac()
                packet.set_hmac([0]*digest.SHA256Digest.LENGTH)
                hmac = digest.SHA256HMAC(hip_config.config["controller"]["master_secret"])           
                if hmac != hmac.digest(packet.get_buffer()):
                    logging.critical("Invalid HMAC in the packet")
                hosts = packet.get_hosts()
                write_hosts_to_file(hosts)
            else:
                logging.debug("Invalid control-plane packet type")

def heart_beat_loop():
    """
    Heart beat loop: 
        send periodic registration messages to the cloud (this includes HIT and IP address)
    """
    try:
        hip_config_socket_lock.acquire();
        if not hip_config_socket:
            hip_config_socket = open_controller_socket();
    except:
        pass
    finally:
        hip_config_socket_lock.release();
    while True:
        nonce = os.urandom(4);
        hit = hiplib.get_own_hit();
        ip = misc.Utils.ipv4_to_int(hip_config.config["swtich"]["source_ip"]);
        heartbeat = Controller.HeartbeatPacket();
        heartbeat.set_packet_type(Controller.HEART_BEAT_TYPE);
        heartbeat.set_hit(hit);
        heartbeat.set_ip(ip);
        heartbeat.set_packet_length(Controller.HEART_BEAT_LENGTH_LENGTH);
        heartbeat.set_nonce(nonce);
        buf = heartbeat.get_buffer();
        hmac = digest.SHA256HMAC(hip_config.config["controller"]["master_secret"])
        digest = hmac.digest(buf)
        heartbeat.set_hmac(digest)
        bytes_sent = hip_config_socket.send(heartbeat.get_buffer());
        if bytes_sent == 0:
            try:
                hip_config_socket_lock.acquire();
                if not hip_config_socket:
                    hip_config_socket = open_controller_socket();
            except:
                pass
            finally:
                hip_config_socket_lock.release();
        sleep(hip_config.config["controller"]["heartbeat_interval"]);

def hip_loop():
    while True:
        try:
            logging.debug("Got HIP packet on the interface")
            packet = bytearray(hip_socket.recv(1518))
            packets = hiplib.process_hip_packet(packet);
            for (packet, dest) in packets:
                hip_socket.sendto(packet, dest)
        except Exception as e:
            logging.debug("Exception occured while processing HIP packet")
            logging.debug(e)

def ip_sec_loop():
    while True:
        try:
            es = time()
            s = time()
            packet = bytearray(ip_sec_socket.recv(1518));
            e = time()
            #logging.info("IPSEC recv time %f " % (e-s))
            s = time()
            (frame, src, dst) = hiplib.process_ip_sec_packet(packet)
            e = time()
            #logging.info("IPSEC process time %f " % (e-s))
            if not frame:
                continue;
            s = time()
            ether_socket.send(frame);
            e = time()
            #logging.info("L2 send time %f " % (e-s))
            frame = Ethernet.EthernetFrame(frame);
            fib.set_next_hop(frame.get_source(), src, dst);
            #logging.debug("Got frame in IPSec loop sending to L2 %s %s....", hexlify(frame.get_source()), hexlify(frame.get_destination()))
            ee = time()
            #logging.info("Total time to process the IPSEC packet %f" % (ee - es))
        except Exception as e:
            logging.critical(e)

def ether_loop():
    while True:
        try:
            s = time()
            buf = bytearray(ether_socket.recv(1518));
            e = time()
            #logging.info("Ethernet recv time %f " % (e-s))
            frame = Ethernet.EthernetFrame(buf);
            dst_mac = frame.get_destination();
            src_mac = frame.get_source();

            #logging.debug("Got data on Ethernet link L2 %s %s..." % (hexlify(src_mac), hexlify(dst_mac)))

            #logging.debug(hexlify(src_mac))
            #logging.debug(hexlify(dst_mac))

            #logging.debug("----------------------------------")
            es = time()
            mesh = fib.get_next_hop(dst_mac);
            for (ihit, rhit) in mesh:
                s = time()
                packets = hiplib.process_l2_frame(frame, ihit, rhit, hip_config.config["swtich"]["source_ip"]);
                e = time()
                #logging.info("L2 process time %f " % (e-s))
                for (hip, packet, dest) in packets:
                    #logging.debug("Sending L2 frame to: %s %s" % (hexlify(ihit), hexlify(rhit)))
                    if not hip:
                        s = time()
                        ip_sec_socket.sendto(packet, dest)
                        e = time()
                        #logging.info("IPSEC send time %f " % (e-s))
                    else:
                        hip_socket.sendto(packet, dest)
            ee = time()
            #logging.info("Total time to process Ethernet frame %f" % (ee-es))
        except Exception as e:
           logging.debug("Exception occured while processing L2 frame")
           logging.debug(e)


# Register exit handler
atexit.register(onclose);

hip_th_loop = threading.Thread(target = hip_loop, args = (), daemon = True);
ip_sec_th_loop = threading.Thread(target = ip_sec_loop, args = (), daemon = True);
ether_if_th_loop = threading.Thread(target = ether_loop, args = (), daemon = True);
heart_beat_th_loop = threading.Thread(target = heart_beat_loop, args = (), daemon = True);
config_th_loop = threading.Thread(target = config_loop, args = (), daemon = True);

logging.info("Starting the CuteHIP");

hip_th_loop.start();
ip_sec_th_loop.start();
ether_if_th_loop.start();
heart_beat_th_loop.start();
config_th_loop.start();

def run_swtich():
    while True:
        try:
            packets = hiplib.maintenance();
            for (packet, dest) in packets:
                hip_socket.sendto(packet, dest)
            logging.debug("...Periodic cleaning task...")
            sleep(1);
        except Exception as e:
            logging.critical("Exception occured while processing HIP packets in maintenance loop")
            logging.critical(e);
            sleep(1)

run_swtich()

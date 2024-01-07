#!/usr/bin/python3

# Copyright (C) 2019 strangebit

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

class ControllerPacket():
    def __init__(self):
        pass

HEART_BEAT_TYPE_OFFSSET = 0
HEART_BEAT_TYPE_LENGTH = 4
HEART_BEAT_LENGTH_OFFSET = 4
HEART_BEAT_LENGTH_LENGTH = 4
HEART_BEAT_HMAC_OFFSET = 8
HEART_BEAT_HMAC_LENGTH = 16
HEART_BEAT_NONCE_OFFSET = 24
HEART_BEAT_NONCE_LENGTH = 4
HEART_BEAT_HIT_OFFSET = 28
HEART_BEAT_HIT_LENGTH = 16
HEART_BEAT_IP_OFFSET = 44
HEART_BEAT_IP_LENGTH = 4

class HeartbeatPacket(ControllerPacket):
    def __init__(self, buffer):
        if not buffer:
            self.buffer = bytearray([0] * (HEART_BEAT_TYPE_LENGTH +
                                           HEART_BEAT_LENGTH_LENGTH +
                                           HEART_BEAT_HMAC_LENGTH +
                                           HEART_BEAT_NONCE_LENGTH +
                                           HEART_BEAT_HIT_LENGTH +
                                           HEART_BEAT_IP_LENGTH))
        else:
            self.buffer = buffer
    def set_packet_type(self, type):
        self.buffer[HEART_BEAT_TYPE_OFFSSET] = (type >> 24) & 0xFF;
        self.buffer[HEART_BEAT_TYPE_OFFSSET + 1] = (type >> 16) & 0xFF;
        self.buffer[HEART_BEAT_TYPE_OFFSSET + 2] = (type >> 8) & 0xFF;
        self.buffer[HEART_BEAT_TYPE_OFFSSET + 3] = type & 0xFF;
    def get_packet_type(self):
        type = 0
        type = self.buffer[HEART_BEAT_TYPE_OFFSSET]
        type = (type << 8) | self.buffer[HEART_BEAT_TYPE_OFFSSET + 1];
        type = (type << 8) | self.buffer[HEART_BEAT_TYPE_OFFSSET + 2];
        type = (type << 8) | self.buffer[HEART_BEAT_TYPE_OFFSSET + 3];
        return type
    def set_packet_length(self, length):
        self.buffer[HEART_BEAT_LENGTH_OFFSET] = (length >> 24) & 0xFF;
        self.buffer[HEART_BEAT_LENGTH_OFFSET + 1] = (length >> 16) & 0xFF;
        self.buffer[HEART_BEAT_LENGTH_OFFSET + 2] = (length >> 8) & 0xFF;
        self.buffer[HEART_BEAT_LENGTH_OFFSET + 3] = length & 0xFF;
    def get_packet_type(self):
        length = 0
        length = self.buffer[HEART_BEAT_LENGTH_OFFSET]
        length = (length << 8) | self.buffer[HEART_BEAT_LENGTH_OFFSET + 1];
        length = (length << 8) | self.buffer[HEART_BEAT_LENGTH_OFFSET + 2];
        length = (length << 8) | self.buffer[HEART_BEAT_LENGTH_OFFSET + 3];
        return length
    def set_hmac(self, hmac):
        self.buffer[HEART_BEAT_HMAC_OFFSET:HEART_BEAT_HMAC_OFFSET + HEART_BEAT_HMAC_LENGTH] = hmac
    def get_hmac(self):
        return self.buffer[HEART_BEAT_HMAC_OFFSET:HEART_BEAT_HMAC_OFFSET + HEART_BEAT_HMAC_LENGTH]
    def set_nonce(self, nonce):
        self.buffer[HEART_BEAT_NONCE_OFFSET:HEART_BEAT_NONCE_OFFSET + HEART_BEAT_NONCE_LENGTH] = nonce
    def get_nonce(self)
        return self.buffer[HEART_BEAT_NONCE_OFFSET:HEART_BEAT_NONCE_OFFSET + HEART_BEAT_NONCE_LENGTH]
    def set_hit(self, hit):
        self.buffer[HEART_BEAT_HIT_OFFSET:HEART_BEAT_HIT_OFFSET + HEART_BEAT_HIT_LENGTH] = nonce
    def get_hit(self):
        return self.buffer[HEART_BEAT_HIT_OFFSET:HEART_BEAT_HIT_OFFSET + HEART_BEAT_HIT_LENGTH]
    def set_ip(self, ip):
        self.buffer[HEART_BEAT_IP_OFFSET:HEART_BEAT_IP_OFFSET + HEART_BEAT_IP_LENGTH] = ip
    def get_ip(self):
        return self.buffer[HEART_BEAT_IP_OFFSET:HEART_BEAT_IP_OFFSET + HEART_BEAT_IP_LENGTH]
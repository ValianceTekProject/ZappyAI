##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## message
##

## Updated encryption in teams/message.py
import json
import base64
import time
import zlib
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from utils.logger import logger

class MessageType(Enum):
    STATUS = "status"
    INCANTATION_REQUEST = "incant_req"
    INCANTATION_RESPONSE = "incant_resp"
    RESOURCE_REQUEST = "resource_req"
    RESOURCE_RESPONSE = "resource_resp"
    DEFENSE_REQUEST = "defense_req"

class Message:
    # Shared secret key (rotate per deployment)
    _SECRET_KEY = b"s3cr3t_team_key_2025"
    _KEY_STREAM_SIZE = 256

    @staticmethod
    def _derive_keystream(length: int) -> bytes:
        """
        Simple keystream: zlib-crc32 of secret + timestamp cycles to fill length
        """
        key = Message._SECRET_KEY
        buf = bytearray()
        t = int(time.time())
        idx = 0
        while len(buf) < length:
            chunk = zlib.crc32(key + t.to_bytes(8, 'big') + idx.to_bytes(4, 'big'))
            buf.extend(chunk.to_bytes(4, 'big'))
            idx += 1
        return bytes(buf[:length])

    @staticmethod
    def _xor_rotate(data: bytes) -> bytes:
        ks = Message._derive_keystream(len(data))
        out = bytearray(len(data))
        for i, b in enumerate(data):
            x = b ^ ks[i]
            out[i] = ((x << 3) & 0xFF) | (x >> 5)
        return bytes(out)

    @staticmethod
    def _inv_xor_rotate(data: bytes) -> bytes:
        tmp = bytearray(len(data))
        for i, b in enumerate(data):
            x = ((b >> 3) & 0x1F) | ((b << 5) & 0xE0)
            tmp[i] = x
        ks = Message._derive_keystream(len(data))
        out = bytearray(len(data))
        for i, b in enumerate(tmp):
            out[i] = b ^ ks[i]
        return bytes(out)

    @staticmethod
    def encode_msg(msg_type: MessageType, sender_id: int, payload: Dict[str, Any]) -> str:
        message = {
            "type": msg_type.value,
            "sender_id": sender_id,
            "payload": payload
        }
        raw = json.dumps(message, separators=(",", ":")).encode('utf-8')
        compressed = zlib.compress(raw)
        encrypted = Message._xor_rotate(compressed)
        token = base64.b64encode(encrypted).decode('ascii')
        return token

    @staticmethod
    def decode_msg(token: str) -> Optional[Tuple[MessageType, int, Dict[str, Any]]]:
        try:
            encrypted = base64.b64decode(token)
            compressed = Message._inv_xor_rotate(encrypted)
            raw = zlib.decompress(compressed).decode('utf-8')
            msg = json.loads(raw)
            msg_type = MessageType(msg["type"])
            sender_id = int(msg.get("sender_id", 0))
            payload = msg.get("payload", {})
            return msg_type, sender_id, payload
        except Exception as e:
            logger.error(f"Failed to decode message: {e}")
            return None

    @staticmethod
    def create_incantation_request(sender_id: int, team_id: str, level: int, required_players: int, timestamp: Optional[float] = None) -> str:
        data = {
            "sender_id": sender_id,
            "team_id": team_id,
            "level": level,
            "required_players": required_players,
            "action": "incant_req",
            "timestamp": timestamp if timestamp is not None else time.time()
        }
        return Message.encode_msg(MessageType.INCANTATION_REQUEST, sender_id, data)

    @staticmethod
    def create_incantation_response(sender_id: int, team_id: str, request_sender: int, response: str, level: int, eta: Optional[int] = None, timestamp: Optional[float] = None) -> str:
        data: Dict[str, Any] = {
            "sender_id": sender_id,
            "team_id": team_id,
            "request_sender": request_sender,
            "response": response,
            "action": "incant_resp",
            "level": level,
            "timestamp": timestamp if timestamp is not None else time.time()
        }
        if eta is not None:
            data["eta"] = eta
        return Message.encode_msg(MessageType.INCANTATION_RESPONSE, sender_id, data)

    @staticmethod
    def create_defense_request(sender_id: int, team_id: str, threat_level: str, timestamp: Optional[float] = None) -> str:
        data = {
            "sender_id": sender_id,
            "team_id": team_id,
            "threat_level": threat_level,
            "action": "defense_req",
            "timestamp": timestamp if timestamp is not None else time.time()
        }
        return Message.encode_msg(MessageType.DEFENSE_REQUEST, sender_id, data)

    @staticmethod
    def create_resource_request(sender_id: int, team_id: str, resource: str, quantity: int, timestamp: Optional[float] = None) -> str:
        data = {
            "sender_id": sender_id,
            "team_id": team_id,
            "resource": resource,
            "quantity": quantity,
            "action": "resource_req",
            "timestamp": timestamp if timestamp is not None else time.time()
        }
        return Message.encode_msg(MessageType.RESOURCE_REQUEST, sender_id, data)

    @staticmethod
    def create_resource_response(sender_id: int, team_id: str, request_sender: int, resource: str, status: str, eta: Optional[int] = None, timestamp: Optional[float] = None) -> str:
        data = {
            "sender_id": sender_id,
            "team_id": team_id,
            "request_sender": request_sender,
            "resource": resource,
            "status": status,  # e.g., 'on_way', 'unavailable', 'delivered'
            "action": "resource_resp",
            "timestamp": timestamp if timestamp is not None else time.time()
        }
        if eta is not None:
            data["eta"] = eta
        return Message.encode_msg(MessageType.RESOURCE_RESPONSE, sender_id, data)

    @staticmethod
    def is_message_expired(timestamp: float, max_age: float = 60.0) -> bool:
        return (time.time() - timestamp) > max_age

    @staticmethod
    def get_message_age(timestamp: float) -> float:
        return time.time() - timestamp

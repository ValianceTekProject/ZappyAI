##
## EPITECH PROJECT, 2025
## Zappy
## File description:
## message
##

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
    _SECRET_KEY = b"s3cr3t_team_key_2025"

    @staticmethod
    def _derive_keystream(length: int) -> bytes:
        """Dérive un keystream simple et robuste."""
        key = Message._SECRET_KEY
        buf = bytearray()
        t = int(time.time()) & 0xFFFF
        idx = 0
        while len(buf) < length:
            chunk = zlib.crc32(key + t.to_bytes(4, 'big') + idx.to_bytes(4, 'big'))
            buf.extend(chunk.to_bytes(4, 'big', signed=False))
            idx += 1
        return bytes(buf[:length])

    @staticmethod
    def _xor_rotate(data: bytes) -> bytes:
        """Chiffrement XOR + rotation robuste."""
        if not data:
            return b''
        
        ks = Message._derive_keystream(len(data))
        out = bytearray(len(data))
        for i, b in enumerate(data):
            x = b ^ ks[i]
            out[i] = ((x << 3) & 0xFF) | (x >> 5)
        return bytes(out)

    @staticmethod
    def _inv_xor_rotate(data: bytes) -> bytes:
        """Déchiffrement inverse robuste."""
        if not data:
            return b''
            
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
        """Encode un message avec gestion d'erreur robuste."""
        try:
            message = {
                "type": msg_type.value,
                "sender_id": sender_id,
                "payload": payload
            }
            
            raw = json.dumps(message, separators=(",", ":"), ensure_ascii=True).encode('utf-8')
            
            compressed = zlib.compress(raw, level=1)
            
            encrypted = Message._xor_rotate(compressed)
            
            token = base64.b64encode(encrypted).decode('ascii')
            
            return token
            
        except Exception as e:
            logger.error(f"[Message] Erreur encodage: {e}")
            return ""

    @staticmethod
    def decode_msg(token: str) -> Optional[Tuple[MessageType, int, Dict[str, Any]]]:
        """Décode un message avec validation robuste."""
        try:
            if not token or not token.strip():
                return None
                
            token = token.strip()
            
            token = Message.fix_base64_padding(token)
            
            if len(token) < 4:
                return None
                
            try:
                encrypted = base64.b64decode(token, validate=True)
            except Exception:
                logger.debug(f"[Message] Échec décodage base64")
                return None
                
            if not encrypted:
                return None
                
            try:
                compressed = Message._inv_xor_rotate(encrypted)
            except Exception:
                logger.debug(f"[Message] Échec déchiffrement")
                return None
                
            if not compressed:
                return None
                
            try:
                raw = zlib.decompress(compressed)
            except zlib.error as e:
                logger.debug(f"[Message] Échec décompression zlib: {e}")
                return None
            except Exception as e:
                logger.debug(f"[Message] Erreur décompression: {e}")
                return None
                
            try:
                json_str = raw.decode('utf-8')
            except UnicodeDecodeError:
                logger.debug(f"[Message] Échec décodage UTF-8")
                return None
                
            try:
                msg = json.loads(json_str)
            except json.JSONDecodeError:
                logger.debug(f"[Message] Échec parsing JSON")
                return None
                
            if not isinstance(msg, dict):
                return None
                
            msg_type_str = msg.get("type")
            if not msg_type_str:
                return None
                
            try:
                msg_type = MessageType(msg_type_str)
            except ValueError:
                logger.debug(f"[Message] Type de message inconnu: {msg_type_str}")
                return None
                
            sender_id = msg.get("sender_id", 0)
            payload = msg.get("payload", {})
            
            if not isinstance(payload, dict):
                payload = {}
                
            logger.debug(f"[Message] ✅ Message décodé: {msg_type_str} de {sender_id}")
            return msg_type, int(sender_id), payload
            
        except Exception as e:
            logger.debug(f"[Message] Erreur générale décodage: {e}")
            return None

    @staticmethod
    def fix_base64_padding(token: str) -> str:
        """Corrige le padding base64."""
        if not token:
            return token
        missing_padding = (4 - len(token) % 4) % 4
        return token + '=' * missing_padding

    @staticmethod
    def create_incantation_request(sender_id: int, team_id: str, level: int, required_players: int, timestamp: Optional[float] = None) -> str:
        """Crée une requête d'incantation."""
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
        """Crée une réponse d'incantation."""
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
        """Crée une demande de défense."""
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
        """Crée une demande de ressources."""
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
        """Crée une réponse de ressources."""
        data = {
            "sender_id": sender_id,
            "team_id": team_id,
            "request_sender": request_sender,
            "resource": resource,
            "status": status,
            "action": "resource_resp",
            "timestamp": timestamp if timestamp is not None else time.time()
        }
        if eta is not None:
            data["eta"] = eta
        return Message.encode_msg(MessageType.RESOURCE_RESPONSE, sender_id, data)

    @staticmethod
    def is_message_expired(timestamp: float, max_age: float = 60.0) -> bool:
        """Vérifie si un message a expiré."""
        return (time.time() - timestamp) > max_age

    @staticmethod
    def get_message_age(timestamp: float) -> float:
        """Retourne l'âge d'un message."""
        return time.time() - timestamp
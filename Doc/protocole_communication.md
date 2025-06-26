
# 🛰️ Protocole de communication – Zappy

## 📋 Objectif
Ce protocole permet aux intelligences artificielles (IA) d'une équipe de communiquer efficacement et de manière sécurisée dans le projet **Zappy**.
Il couvre :
- La structure des messages
- Les différents types de messages
- Le mécanisme de chiffrement
- Comment décrypter un message manuellement

---

## 🧱 Structure d’un message (avant chiffrement)

Chaque message est un dictionnaire JSON compressé, contenant :

```json
{
  "type": "<message_type>",
  "sender_id": <int>,
  "payload": {
    ... contenu spécifique au type de message ...
  }
}
```

### Champs principaux :
- **type** : un identifiant de type (voir ci-dessous)
- **sender_id** : identifiant unique du bot émetteur
- **payload** : informations spécifiques au message

---

## 📡 Types de messages supportés

| Type                     | Nom interne        | Utilité |
|--------------------------|--------------------|--------|
| `status`                | `STATUS`           | État général d’un bot |
| `incant_req`            | `INCANTATION_REQUEST` | Demande de début d’incantation |
| `incant_resp`           | `INCANTATION_RESPONSE` | Réponse à une demande d’incantation |
| `defense_req`           | `DEFENSE_REQUEST`  | Demande d’aide pour défense |
| `resource_req`          | `RESOURCE_REQUEST` | Demande de ressources |
| `resource_resp`         | `RESOURCE_RESPONSE` | Réponse à une demande de ressources |

---

## 🔐 Mécanisme de chiffrement/déchiffrement

Chaque message suit **quatre étapes de transformation** avant transmission :
1. **Sérialisation JSON** (compact, sans indentation)
2. **Compression zlib**
3. **Chiffrement XOR + rotation de bits**
4. **Encodage base64**

### 🗝️ Clé secrète partagée
Clé codée en dur :  
`b"s3cr3t_team_key_2025"`  
**⚠️ À changer pour chaque déploiement**

---

## 🔄 Étapes détaillées

### 1. JSON Compact
Le message est converti en une chaîne JSON compacte (sans espaces), par exemple :

```json
{"type":"incant_req","sender_id":2,"payload":{"team_id":"blue","level":3,...}}
```

---

### 2. Compression zlib
Le JSON est compressé via l’algorithme `zlib`.

---

### 3. Chiffrement : XOR + rotation de bits
#### a. Dérivation du keystream
- Un keystream est généré à partir de la clé secrète, de l'heure actuelle (`time.time()`) et d’un index croissant.
- Pour chaque bloc de 4 octets :
  ```python
  crc32(secret + timestamp_bytes + index_bytes)
  ```

#### b. Application du chiffrement
- Chaque octet du message est XORé avec l’octet correspondant du keystream.
- Puis, chaque octet est **roté de 3 bits vers la gauche**.

**Exemple sur un octet :**
```
Original :      0b10100110
XOR stream :    0b00111010
Résultat XOR :  0b10011100
Rotation gauche (<< 3) : 0b11100100
```

---

### 4. Encodage Base64
Le message chiffré est encodé en base64 pour permettre sa transmission sous forme de texte (ASCII).

---

## 🔓 Déchiffrement (à l’identique)

Pour déchiffrer un message reçu :
1. **Décoder en base64**
2. **Rotation de bits vers la droite (>> 3)**
3. **XOR avec le même keystream**
4. **Décompresser avec zlib**
5. **Parser le JSON**

---

## 🧪 Exemple de payloads

### ✨ Incantation (requête)
```json
{
  "sender_id": 2,
  "team_id": "blue",
  "level": 3,
  "required_players": 4,
  "action": "incant_req",
  "timestamp": 1723451111.17
}
```

---

### 🛡️ Demande de défense
```json
{
  "sender_id": 3,
  "team_id": "red",
  "threat_level": "high",
  "action": "defense_req",
  "timestamp": 1723451122.44
}
```

---

### 🪙 Demande de ressources
```json
{
  "sender_id": 5,
  "team_id": "blue",
  "resource": "linemate",
  "quantity": 2,
  "action": "resource_req",
  "timestamp": 1723451133.99
}
```

---

## ⌛ Validité temporelle des messages
- Un message est considéré **expiré après 60 secondes** (`max_age = 60.0`)
- Chaque message contient un `timestamp` Unix flottant (`float`)

---

## ✅ Résumé – Étapes de transmission

| Étape       | Action                                    |
|-------------|--------------------------------------------|
| 1️⃣ JSON     | Sérialisation compacte (`json.dumps(..., separators=(',', ':'))`) |
| 2️⃣ zlib     | Compression avec `zlib.compress(...)`     |
| 3️⃣ Chiffrement | XOR + rotation bits gauche (3)         |
| 4️⃣ base64   | Encodage base64                           |
| 📤 Envoi     | Transmission par texte                    |

---

## 📥 À noter

- Le keystream **change à chaque appel** car il dépend de l’heure actuelle, ce qui rend les messages **non reproductibles** même avec un même contenu.
- La synchronisation des horloges (max 1-2s de dérive) est recommandée pour reproduire le keystream côté client.
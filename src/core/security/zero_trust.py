import os
import jwt
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(
    filename=Path(__file__).resolve().parents[3] / 'logs' / 'audit' / 'security_siem.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [ZERO-TRUST] %(message)s'
)

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'oracle-systems-quantum-secret-8247')

def generate_enterprise_token(client_id: str, tier: str = 'enterprise') -> str:
    payload = {
        'sub': client_id,
        'ein': '82-4737196',
        'tier': tier,
        'exp': datetime.utcnow() + timedelta(hours=12)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    logging.info(f"Generated cryptographic access token for client: {client_id} [Tier: {tier}]")
    return token

def verify_enterprise_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'valid': True, 'payload': payload}
    except Exception as e:
        logging.warning(f"Security violation detected - Invalid token: {e}")
        return {'valid': False, 'error': str(e)}

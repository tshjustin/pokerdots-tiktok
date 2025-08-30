from sqlalchemy import event
from sqlalchemy.orm import Session
from .models import TokenWallet, AppreciationToken
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tops up new wallet with appreciation token
# @event.listens_for(TokenWallet, "after_insert")
# def top_up_wallet(mapper, connection, target):
#     """Create 10 appreciation tokens when a new wallet is created"""
#     # Get the session from the connection
#     db = Session(bind=connection)

#     try:
#         new_tokens = [
#             AppreciationToken(
#                 wallet_id=target.wallet_id,
#                 ip_hash="ip",
#                 source="tap",
#             )
#             for _ in range(10)
#         ]

#         # Add all tokens to the session
#         db.add_all(new_tokens)
#         db.flush()
#         logger.info("Tokens successfully added!")

#     except Exception as e:
#         db.rollback()
#         logger.error(f"An error has occurred while topping up new wallet: {str(e)}")
#         raise e

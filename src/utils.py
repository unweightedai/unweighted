import re
from datetime import datetime, timedelta
import base58
from solders.pubkey import Pubkey

def extract_token_address(text):
    """Extract Solana token addresses from text."""
    # Match base58 encoded Solana addresses
    pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
    addresses = re.findall(pattern, text)
    
    # Validate addresses
    valid_addresses = []
    for addr in addresses:
        try:
            pubkey = Pubkey.from_string(addr)
            valid_addresses.append(str(pubkey))
        except:
            continue
            
    return valid_addresses

def calculate_roi(initial_price, current_price):
    """Calculate ROI percentage."""
    if initial_price == 0:
        return 0
    return ((current_price - initial_price) / initial_price) * 100

def format_sol_address(address):
    """Format and validate Solana address."""
    try:
        if isinstance(address, str):
            return str(Pubkey.from_string(address))
        elif isinstance(address, Pubkey):
            return str(address)
        else:
            raise ValueError("Invalid address format")
    except:
        raise ValueError("Invalid Solana address")

def format_price(price, decimals=9):
    """Format token price with appropriate decimal places."""
    if price > 1:
        return f"${price:.2f}"
    return f"${price:.{decimals}f}"

def calculate_trust_impact(performance_data):
    """Calculate impact on trust score based on token performance."""
    roi = performance_data.get('roi', 0)
    liquidity_change = performance_data.get('liquidity_change', 0)
    holder_change = performance_data.get('holder_change', 0)
    
    impact = 0
    
    # Positive impacts
    if roi > 50:
        impact += 5
    elif roi > 20:
        impact += 3
    elif roi > 0:
        impact += 1
        
    # Negative impacts
    if roi < -50:
        impact -= 5
    elif roi < -20:
        impact -= 3
        
    if liquidity_change < -50:
        impact -= 5
        
    return impact

def is_program_derived_address(address):
    """Check if address is a PDA."""
    try:
        return len(base58.b58decode(address)) > 32
    except:
        return False
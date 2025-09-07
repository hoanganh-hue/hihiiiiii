"""
Module for calculating and validating the checksum digit of a Vietnamese Citizen ID (CCCD).
The algorithm is based on Thông tư 07/2016/TT-BCA.
This is a Luhn-like algorithm with specific weights.
"""

def calculate_checksum(cccd_eleven_digits: str) -> int:
    """
    Calculates the checksum for the first 11 digits of a CCCD.
    The weights are 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1.
    """
    if not cccd_eleven_digits.isdigit() or len(cccd_eleven_digits) != 11:
        raise ValueError("Input must be a string of 11 digits.")
    
    weights = [1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1]
    total = sum(int(digit) * weight for digit, weight in zip(cccd_eleven_digits, weights))
    
    checksum = (10 - (total % 10)) % 10
    return checksum

def is_checksum_valid(cccd: str) -> bool:
    """
    Checks if the last digit of a 12-digit CCCD is a valid checksum.
    """
    if not cccd.isdigit() or len(cccd) != 12:
        return False
    
    try:
        eleven_digits = cccd[:-1]
        last_digit = int(cccd[-1])
        return calculate_checksum(eleven_digits) == last_digit
    except ValueError:
        return False

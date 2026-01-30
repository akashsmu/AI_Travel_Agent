import re
import logging
from typing import Tuple

logger = logging.getLogger("security_manager")

class SecurityManager:
    """
    Handles input sanitization, PII masking, and basic prompt injection detection.
    """
    
    def __init__(self):
        # Regex patterns for PII
        self.pii_patterns = {
            "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "passport": r"\b[A-Z0-9]{6,9}\b" # Generic passport pattern
        }
        
        # Heuristic keywords for Prompt Injection / Jailbreak
        self.injection_keywords = [
            "ignore previous instructions",
            "ignore all instructions",
            "system prompt",
            "you are now DAN",
            "do anything now",
            "jailbreak",
            "developer mode",
            "disable safety"
        ]

    def sanitize_input(self, text: str) -> str:
        """
        Masks PII in the input text.
        """
        sanitized_text = text
        for pii_type, pattern in self.pii_patterns.items():
            sanitized_text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", sanitized_text)
            
        if sanitized_text != text:
            logger.info(f"🛡️ PII detected and redacted in input.")
            
        return sanitized_text

    def detect_injection(self, text: str) -> bool:
        """
        Checks for potential prompt injection attempts.
        Returns True if injection is suspected.
        """
        lower_text = text.lower()
        for keyword in self.injection_keywords:
            if keyword in lower_text:
                logger.warning(f"🚨 Potential Prompt Injection detected: '{keyword}'")
                return True
        return False

    def validate_and_clean(self, text: str) -> Tuple[bool, str]:
        """
        Full pass: Detect injection -> Sanitize PII.
        Returns (is_safe, cleaned_text).
        If injection detected, is_safe=False and text is empty or warning.
        """
        if self.detect_injection(text):
            return False, "Input blocked due to safety policies."
            
        return True, self.sanitize_input(text)

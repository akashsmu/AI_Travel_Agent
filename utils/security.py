import re
import logging
from typing import Tuple

logger = logging.getLogger("security_manager")

from deepeval.metrics import ToxicityMetric
from deepeval.test_case import LLMTestCase

class SecurityManager:
    """
    Handles input sanitization, PII masking, and basic prompt injection detection.
    Also uses DeepEval for toxicity/harmful content detection.
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

        # Initialize DeepEval Metric
        # Note: threshold 0.5 means if it's > 50% toxic, it fails.
        self.toxicity_metric = ToxicityMetric(threshold=0.5)

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

    def detect_harmful_content(self, text: str) -> bool:
        """
        Uses DeepEval to detect toxic or harmful content.
        Returns True if harmful.
        """
        try:
            # DeepEval expects an 'LLMTestCase'
            test_case = LLMTestCase(
                input=text, 
                actual_output=text # minimal needed mostly for metric internal structure
            )
            
            self.toxicity_metric.measure(test_case)
            
            # If successful (score is low enough), success is True.
            # If toxic, success is False.
            if not self.toxicity_metric.is_successful():
                logger.warning(f"🚨 Toxic content detected! Score: {self.toxicity_metric.score}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"DeepEval check failed: {e}")
            # Fail open or closed? Let's fail open for now to not block if service is down,
            # but log heavily.
            return False

    def validate_and_clean(self, text: str) -> Tuple[bool, str]:
        """
        Full pass: Detect injection -> Detect Harmful -> Sanitize PII.
        Returns (is_safe, cleaned_text).
        If blocked, is_safe=False and text is warning.
        """
        if self.detect_injection(text):
            return False, "Input blocked due to projection injection policies."
            
        if self.detect_harmful_content(text):
            return False, "Input blocked due to harmful/toxic content policies."
            
        return True, self.sanitize_input(text)

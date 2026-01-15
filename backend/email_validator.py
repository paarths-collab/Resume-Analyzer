import re
import dns.resolver
from typing import Tuple

# List of common disposable email domains
DISPOSABLE_EMAIL_DOMAINS = {
    'tempmail.com', 'guerrillamail.com', 'mailinator.com', '10minutemail.com',
    'throwaway.email', 'maildrop.cc', 'temp-mail.org', 'yopmail.com',
    'fakeinbox.com', 'trashmail.com', 'getnada.com', 'tempmailaddress.com',
    'emailondeck.com', 'spam4.me', 'mytemp.email', 'tempinbox.com',
    'mohmal.com', 'sharklasers.com', 'guerrillamail.info', 'grr.la',
    'guerrillamail.biz', 'guerrillamail.de', 'mintemail.com', 'dispostable.com',
    'spamgourmet.com', 'mailnesia.com', 'getairmail.com', 'meltmail.com',
    'tmpmail.net', 'tmpeml.info', 'anonymbox.com', 'burnermail.io',
    'guerrillamail.net', 'guerrillamail.org', 'mailexpire.com', 'mailforspam.com',
    'mailnull.com', 'mytrashmail.com', 'spambox.us', 'trash-mail.com',
    'rootfest.net', 'noclickemail.com', 'jetable.org', 'anonbox.net',
    'discard.email', 'throwam.com', 'spamfree24.org', 'msgden.net'
}

class EmailValidator:
    
    @staticmethod
    def is_valid_format(email: str) -> bool:
        """Check if email format is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_disposable(email: str) -> bool:
        """Check if email is from a disposable email provider"""
        domain = email.split('@')[-1].lower()
        return domain in DISPOSABLE_EMAIL_DOMAINS
    
    @staticmethod
    def has_mx_record(domain: str) -> bool:
        """Check if domain has valid MX records"""
        try:
            dns.resolver.resolve(domain, 'MX')
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return False
        except Exception:
            # If DNS check fails for other reasons, allow it
            return True
    
    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, str]:
        """
        Email validation - simplified for now
        Returns: (is_valid, error_message)
        """
        # Format validation
        if not cls.is_valid_format(email):
            return False, "Invalid email format"
        
        # Disposable email check
        if cls.is_disposable(email):
            return False, "Disposable email addresses are not allowed"
        
        # Skip DNS check for now - it can cause timeouts
        return True, ""

email_validator = EmailValidator()
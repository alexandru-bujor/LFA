import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List

class TokenType(Enum):
    IPV4_ADDRESS    = auto()
    MAC_ADDRESS     = auto()
    STRING          = auto()
    NUMBER          = auto()
    # DSL keywords
    KEYWORD_NETWORK    = auto()
    KEYWORD_DEVICE     = auto()
    KEYWORD_MODULE     = auto()
    KEYWORD_SLOT       = auto()
    KEYWORD_INTERFACE  = auto()
    KEYWORD_VLAN       = auto()
    KEYWORD_ROUTE      = auto()
    KEYWORD_DHCP       = auto()
    KEYWORD_ACL        = auto()
    KEYWORD_LINK       = auto()
    KEYWORD_COORDINATES= auto()
    KEYWORD_POWER      = auto()
    KEYWORD_GATEWAY    = auto()
    KEYWORD_DNS        = auto()
    KEYWORD_BANDWIDTH  = auto()
    KEYWORD_ALLOW      = auto()
    KEYWORD_DENY       = auto()
    KEYWORD_FROM       = auto()
    KEYWORD_TO         = auto()
    KEYWORD_POOL       = auto()
    KEYWORD_NAME       = auto()
    KEYWORD_DESC       = auto()
    KEYWORD_CABLE      = auto()
    KEYWORD_LENGTH     = auto()
    KEYWORD_FUNCTIONAL = auto()
    KEYWORD_STATIC     = auto()
    # fallback
    ID                = auto()

# Patterns must be tested in order
_token_specs = [
    (TokenType.IPV4_ADDRESS,    re.compile(r'(?:\d{1,3}\.){3}\d{1,3}')),
    (TokenType.MAC_ADDRESS,     re.compile(r'[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}')),
    (TokenType.STRING,          re.compile(r'"[^"]*"')),
    (TokenType.NUMBER,          re.compile(r'\d+')),
    (TokenType.KEYWORD_NETWORK,     re.compile(r'network\b')),
    (TokenType.KEYWORD_DEVICE,      re.compile(r'device\b')),
    (TokenType.KEYWORD_MODULE,      re.compile(r'module\b')),
    (TokenType.KEYWORD_SLOT,        re.compile(r'slot\b')),
    (TokenType.KEYWORD_INTERFACE,   re.compile(r'interface\b')),
    (TokenType.KEYWORD_VLAN,        re.compile(r'vlan\b')),
    (TokenType.KEYWORD_ROUTE,       re.compile(r'route\b')),
    (TokenType.KEYWORD_DHCP,        re.compile(r'dhcp\b')),
    (TokenType.KEYWORD_ACL,         re.compile(r'acl\b')),
    (TokenType.KEYWORD_LINK,        re.compile(r'link\b')),
    (TokenType.KEYWORD_COORDINATES, re.compile(r'coordinates\b')),
    (TokenType.KEYWORD_POWER,       re.compile(r'power\b')),
    (TokenType.KEYWORD_GATEWAY,     re.compile(r'gateway\b')),
    (TokenType.KEYWORD_DNS,         re.compile(r'dns\b')),
    (TokenType.KEYWORD_BANDWIDTH,   re.compile(r'bandwidth\b')),
    (TokenType.KEYWORD_ALLOW,       re.compile(r'allow\b')),
    (TokenType.KEYWORD_DENY,        re.compile(r'deny\b')),
    (TokenType.KEYWORD_FROM,        re.compile(r'from\b')),
    (TokenType.KEYWORD_TO,          re.compile(r'to\b')),
    (TokenType.KEYWORD_POOL,        re.compile(r'pool\b')),
    (TokenType.KEYWORD_NAME,        re.compile(r'name\b')),
    (TokenType.KEYWORD_DESC,        re.compile(r'desc\b')),
    (TokenType.KEYWORD_CABLE,       re.compile(r'cable\b')),
    (TokenType.KEYWORD_LENGTH,      re.compile(r'length\b')),
    (TokenType.KEYWORD_FUNCTIONAL,  re.compile(r'functional\b')),
    (TokenType.KEYWORD_STATIC,      re.compile(r'static\b')),
    (TokenType.ID,                 re.compile(r'[A-Za-z_][A-Za-z0-9_-]*')),
]

@dataclass
class Token:
    type: TokenType
    value: str


def tokenize(text: str) -> List[Token]:
    """
    Scan the input text and return a list of Tokens (type, value),
    matching the first pattern at each position.
    """
    pos = 0
    tokens: List[Token] = []
    length = len(text)
    while pos < length:
        if text[pos].isspace():
            pos += 1
            continue
        for tok_type, pattern in _token_specs:
            m = pattern.match(text, pos)
            if m:
                val = m.group(0)
                tokens.append(Token(tok_type, val))
                pos = m.end()
                break
        else:
            raise SyntaxError(f"Illegal character at position {pos}: '{text[pos]}'")
    return tokens

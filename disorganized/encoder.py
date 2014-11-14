"""
encoder
=======
Encode and decode numbers to unguessable strings. For use in urls, so that
our API does not reveal incremental ids
"""

from .treeprng import treeprng

DEFAULT_ALPHABET = 'ozWDIKGwfBrVnJ52dcsub3elg69ERkmpFh1jiSCaXyUPMTYZQqt47HvLxANO8'
DEFAULT_BLOCK_SIZE = 22

def alphagen(key, alphabet=None):
    t = treeprng.TreePRNG()['django_rest_framework']['non-sequential']
    if alphabet is None:
        alphabet = list(DEFAULT_ALPHABET)
    else:
        alphabet = list(alphabet)
    t[key].shuffle(alphabet)
    return ''.join(alphabet)

class UrlEncoder(object):
    
    def __init__(self, key=None, alphabet=None, block_size=None):
        if alphabet is None:
            alphabet = DEFAULT_ALPHABET
        if block_size is None:
            self.block_size = DEFAULT_BLOCK_SIZE
        else:
            self.block_size = block_size
        if key is not None:
            # generate new alphabet from key
            self.alphabet = alphagen(key, alphabet)
        else:
            self.alphabet = alphabet
        self.mask = (1 << self.block_size) - 1
        self.mapping = range(self.block_size)
        self.mapping.reverse()
        
    def encode_url(self, n, min_length=0):
        return self.enbase(self.encode(n), min_length)
    
    def decode_url(self, n):
        return self.decode(self.debase(n))
    
    def encode(self, n):
        return (n & ~self.mask) | self._encode(n & self.mask)
    
    def _encode(self, n):
        result = 0
        for i, b in enumerate(self.mapping):
            if n & (1 << i):
                result |= (1 << b)
        return result
    
    def decode(self, n):
        return (n & ~self.mask) | self._decode(n & self.mask)
    
    def _decode(self, n):
        result = 0
        for i, b in enumerate(self.mapping):
            if n & (1 << b):
                result |= (1 << i)
        return result
    
    def enbase(self, x, min_length=0):
        result = self._enbase(x)
        padding = self.alphabet[0] * (min_length - len(result))
        return '%s%s' % (padding, result)
    
    def _enbase(self, x):
        n = len(self.alphabet)
        if x < n:
            return self.alphabet[x]
        return self.enbase(x/n) + self.alphabet[x%n]
    
    def debase(self, x):
        n = len(self.alphabet)
        result = 0
        for i, c in enumerate(reversed(x)):
            result += self.alphabet.index(c) * (n**i)
        return result

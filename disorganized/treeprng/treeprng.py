#!/usr/bin/env python
""" 
Repeatable virtual trees of pseudorandom numbers.  Alpha test version.

https://github.com/switham/treeprng/wiki/Documentation
https://github.com/switham/treeprng/wiki/Critique
"""

# Copyright (c) 2013-2014 Steve Witham.  All rights reserved.  
# treeprng is available under a BSD license, whose full text is at
#   https://github.com/switham/treeprng/blob/master/LICENSE

# WARNING: You may have noticed that this code calls a cryptographic hash 
# function. That does NOT mean this code is secure. treeprng is NOT a 
# cryptographic pseudorandom number generator. Do NOT use it in a crypto 
# or security-sensitive application.

import hashlib, random
try:
    import cPickle as pickle
except:
    import pickle
import copy

TREEPRNG_DOC_URL = "https://github.com/switham/treeprng/wiki/Documentation"


class TreePRNG(object):
    """
    A virtual tree of nested Python dicts with pseudorandom numbers 
    at the bottom.  See the user guide:
        https://github.com/switham/treeprng/wiki/Documentation

    WARNING:You may have noticed that this code calls a cryptographic
    hash function. That does NOT mean this code is secure. treeprng is 
    NOT a cryptographic pseudorandom number generator. Do NOT use it 
    in a crypto or security-sensitive application.
    """

    def __init__(self, hashname="sha1", sequence_class=None):
        """
        Produce the root of the tree in a "dict" state.
        hashname is one of the names in hashlib.algorithms.
        sequence_class is the type of PRNG to be returned by .sequence().
            The default is treeprng.Hash_PRNG using hashname.
        """
        self.hashname = hashname
        self.sequence_class = sequence_class
        self.__hash = hashlib.new(hashname)
        self.is_dict = True # The root is always a dict.

    def __getitem__(self, key):
        """
        t.__getitem__(key) <==> t[key]
        Given a TreePRNG t,
            t[key]
        Creates an uncommitted daughter TreePRNG object.
        This commits t to be a dict, but otherwise doesn't change t.
        key can be any picklable object, but if you want repeatability 
        across runs of a program, see help(pickle_key).
        """
        assert self.__hash, \
            "Tried to use as a dict after spent. See:\n" \
            + TREEPRNG_DOC_URL + "#the-treeprng-life-cycle"
        self.is_dict = True
        
        child = copy.copy(self)
        child.__hash = self.__hash.copy()
        child.is_dict = False
        child.__hash.update("k" + pickle_key(key))
        return child

    def __check_state(self, method):
        assert self.__hash, \
            "Tried to use ." + method + "() after spent. See:\n" \
            + TREEPRNG_DOC_URL + "#the-treeprng-life-cycle"
        assert not self.is_dict, \
            "Tried to use ." + method + "() after use as a dict. See:\n" \
            + TREEPRNG_DOC_URL + "#the-treeprng-life-cycle"

    def sequence(self, prng_class=None):
        """
        Return a PRNG seeded from this TreePRNG object.
        prng_class is an optional random.Random subclass; the default is
        self.sequence_class  (see __init__()).   self becomes spent.
        """
        self.__check_state("sequence")
        seed = long(self.__hash.hexdigest(), 16)
        self.__hash = None  # Spent.
        prng_class = prng_class or self.sequence_class
        if prng_class:
            return prng_class(seed)
        else:
            return Hash_PRNG(seed, hashname=self.hashname)

    def hash(self):
        """ 
        hash() can be used on an uncommitted or dict TreePRNG.
        It commits self to be a dict.
        """
        assert self.__hash, \
            "Tried to use hash() after spent. See:\n" \
            + TREEPRNG_DOC_URL + "#the-treeprng-life-cycle"
        hash = self.__hash.copy()
        hash.update("h")
        self.is_dict = True
        return long(hash.hexdigest(), 16)

    def __getattr__(self, method):
        """
        This handles calls to any random.Random methods by returning the
        method of the PRNG.  Then self becomes spent.
        """
        self.__check_state(method)
        prng = Hash_PRNG(self.__hash, hashname=self.hashname)
        self.__hash = None  # Spent.
        return getattr(prng, method)

    def getstate(self):
        """ Disabled.  To get the state of this TreePRNG, follow its path. """
        raise NotImplementedError()

    def setstate(self, *args, **kargs):
        """ Disabled.  To set the state, create a new TreePRNG. """
        raise NotImplementedError()

    def seed(self, *args, **kargs):
        """ Disabled.  To seed a PRNG, create a new TreePRNG. """
        raise NotImplementedError()

    def jumpahead(self, *args, **kargs):
        """ 
        Disabled.  For multiple random sources under one node, do:
        source1 = node[key1]
        source2 = node[key2]
        ...
        With a unique key for each source.
        """
        raise NotImplementedError()


class Hash_PRNG(random.Random):
    """ hashlib-based PRNG used internally by the treeprng.TreePRNG class. """

    def __init__(self, seed, hashname="sha1"):
        """
        Like random.Random.__init__(), but
          o  seed is required, not optional.
          o  If hasattr(seed, "hexdigest"), 
                 assume seed is a hashlib object that no one will update().
        """
        self.hashname = hashname
        self.seed(seed)

    def seed(self, seed):
        """
        If hasattr(seed, "hexdigest"), 
            assume seed is a hashlib object that no one will update().
        else
            create a hashlib.new(self.hashname) object 
            and update with the pickled seed.
        """
        if hasattr(seed, "hexdigest"):
            self.base_hash = seed
        else:
            self.base_hash = hashlib.new(self.hashname)
            self.base_hash.update("s" + pickle_key(seed))
        # Note: this is the digest of the base_hash itself, while later
        # chunks of bits (if any) are based on updated copies.  That's okay,
        # digest(base) doesn't let you predict digest(base + morebytes).
        self.bits = long(self.base_hash.hexdigest(), 16)
        self.nbits = self.base_hash.digest_size * 8
        self.i = 1

    def getrandbits(self, k):
        """Return a positive int with k random bits."""
        # The bits shift DOWN, new bits are added at the top.
        while k > self.nbits:
            hash = self.base_hash.copy()
            hash.update("p" + pickle.dumps(self.i))
            self.i += 1
            self.bits += long(hash.hexdigest(), 16) << self.nbits
            self.nbits += hash.digest_size * 8
        result = self.bits & ((1 << k) - 1)
        self.bits >>= k
        self.nbits -= k
        return result

    def random(self):
        return self.getrandbits(53) * 2 ** -53
        
    def jumpahead(self, *args, **kargs):
        """ Raises NotImplementedError.  See help(RandomTreePRNG). """
        raise NotImplementedError()

    def getstate(self,  *args, **kargs):
        """ Raises NotImplementedError.  See help(RandomTreePRNG). """
        raise NotImplementedError()

    def setstate(self,  *args, **kargs):
        """ Raises NotImplementedError.  See help(RandomTreePRNG). """
        raise NotImplementedError()


def pickle_key(k):
    """
    Create an input string for a secure hash, using pickle.
    These basic types convert in a repeatable way with this method:
        None, False, True
        string, unicode string
        float, long, int
        tuple -- empty, or tuple of items that convert repeatably
        list -- empty, or list of items that convert repeatably
    pickle_key_massage() (see) is used to make sure equal-comparing numbers
    become actually equal before pickling.
    """
    return pickle.dumps(pickle_key_massage(k), 2)


def pickle_key_massage(k):
    """
    Return (a possibly massaged copy of) input for pickle_key to make sure
    "equal things are equal".  So far this means: 
        An embedded float is converted to an equal long or int if possible.
        An embedded long is converted to an equal int if possible.
    Where "embedded" means in a (nested) list or tuple...or just k itself.
    Members of classes we aren't sure of (e.g. sets, dicts) are left alone.

    Note: pickle_key_massage, pickle_key, and TreePRNG aren't meant to be
    used with large objects as keys.  But the cost is only temporary storage
    (of both the massaged and picked versions) which is recovered 
    immediately, and time (while the hash digests the pickle).
    """
    if type(k) == list:  # ==, not isinstance -- don't massage subclasses.
        for i, x in enumerate(k):
            y = pickle_key_massage(x)
            if y is not x:
                k = k[:i] + [y] + [pickle_key_massage(z) for z in k[i+1:]]
                break
    elif type(k) == tuple:  # ==, not isinstance -- don't massage subclasses.
        for i, x in enumerate(k):
            y = pickle_key_massage(x)
            if y is not x:
                k = k[:i] + (y,) + \
                   tuple(pickle_key_massage(z) for z in k[i+1:])
                break
    elif isinstance(k, float):
        if k == int(k):  k = int(k)
    elif isinstance(k, long):
        k = int(k)
    return k

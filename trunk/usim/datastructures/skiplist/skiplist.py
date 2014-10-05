#!/bin/env python2.7

"""pyskip.py:  A container class for ordered sets in Python.

  Do not edit this file.  It is extracted automatically from the
  documentation:
    http://www.nmt.edu/tcc/help/lang/python/examples/pyskip/
"""
import random    
#================================================================
# Verification functions
#----------------------------------------------------------------
# children-are-ordered ( x, y ) ==
#   if self.allowDups ->
#       cmp ( key-of ( x ), key-of ( y ) ) <= 0
#   else ->
#       cmp ( key-of ( x ), key-of ( y ) ) < 0
#--
# Similar to the keys-are-ordered predicate, but operates on
# child objects.
#----------------------------------------------------------------
# insertion-cut-list ( key ) ==
#   a list L of size self.__maxLevels, such that each element
#   L[i] equals insertion-point ( i, key )
#--
#   An ``insertion cut list'' is a list of the _SkipItem objects
#   that must be updated when a new elements is inserted.  Element
#   [i] of the cut list points to the element whose forward
#   pointer has to be repaired in the (i)th list.
#----------------------------------------------------------------
# insertion-point ( level, key ) ==
#   the last element E in nth-list ( self.__heads, level ) such
#   that insertion-precedes ( E, key ) is true
#--
#   This describes the predecessor _SkipItem whose forward link
#   must be updated when a new item with key (key) is inserted.
#----------------------------------------------------------------
# insertion-point-after ( level, key, searchItem ) ==
#   the last element E in nth-list(searchItem,level) such that
#   insertion-precedes(E, key) is true
#--
#   Just like insertion-point(), except that it starts at an
#   arbitrary _SkipItem instead of self.__heads.
#----------------------------------------------------------------
# insertion-precedes ( skipItem, key ) ==
#   if skipItem is self.__terminator -> F
#   else if skipItem is self.__heads -> T
#   else ->
#     keys-are-ordered ( key-of ( skipItem's child ), key )
#--
#   This predicate is true when (skipItem) should be before
#   an item with key (key) in the level-0 list.
#----------------------------------------------------------------
# key-of ( child ) ==
#   if  not self.keyFunction ->
#       child
#   else ->
#       self.keyFunction ( child )
#----------------------------------------------------------------
# keys-are-ordered ( x, y ) ==
#   if self.allowDups ->
#       cmp ( x, y ) <= 0
#   else ->
#       cmp ( x, y ) < 0
#--
#   This is the ordering relation used in the key domain.
#   -   If we don't allow duplicates, then each key must be
#       strictly less than its successor.
#   -   If we allow duplicates, then two successive keys can
#       be equal.
#----------------------------------------------------------------
# nth-list ( root, n ) ==
#   the linked list of _SkipItem objects rooted at (root) and
#   using _SkipItem.links[n] as the next-item method
#--
#   This define is used to describe positions in the linked list
#   of objects at one level of the structure.  In particular,
#       nth-list ( self.__heads, n )
#   describes the entire skip list at level (n).
#----------------------------------------------------------------
# search-cut-list ( key ) ==
#   a list L of size self.__maxLevels such that
#   L[i] := search-point ( i, key )
#--
#   Like insert-cut-list(), but used for .delete() and .find()
#   operations.
#----------------------------------------------------------------
# search-point ( level, key ) ==
#   the last _SkipItem E in nth-list(self.__heads, level) such that
#   search-precedes(E, key) is true
#--
#   The predecessor whose forward link must be updated when
#   the item with key (key) is deleted.  Also used in
#   .find().
#----------------------------------------------------------------
# search-point-after ( level, key, searchItem ) ==
#   the last element E in nth-list(searchItem, level) such that
#   search-precedes(E, key) is true
#--
#   Like search-point except that the search starts at some
#   given item rather than at self.__heads.
#----------------------------------------------------------------
# search-precedes ( skipItem, key ) ==
#   if skip-compare ( skipitem, key ) < 0  ->  true
#   else -> false
#--
#   A predicate, true when the child in skipItem is before the
#   key (key).
#----------------------------------------------------------------
# skip-compare ( skipItem, key ) ==
#   if skipItem is self.__terminator -> 1
#   else -> cmp ( key-of ( skipItem's child ), key )
#--
#   Like cmp(), but we want to avoid trying to extract a key
#   from self.__terminator, because it doesn't have one.  If
#   skipItem is the terminator, we return 1 because the terminator
#   goes after all other elements.
#----------------------------------------------------------------
# - - - - -   c l a s s   _ S k i p I t e m   - - - - -

class _SkipItem:
    """Represents one child element of a SkipList.

      Exports:
        _SkipItem ( child, nLevels ):
          [ (child is a child object) and
            (nLevels is an integer >= 1) ->
              return a new _SkipItem with that child object and
              (nLevels) forward links, each set to None ]
        .child:        [ as passed to constructor, read-only ]
        .links:
          [ if self is an active SkipList element ->
              a list of nLevels elements, read-write, containing
              pointers to a _SkipItem instance
            else ->
              a list of at least 1 whose first element is None ]
    """
    __slots__ = ('child', 'links')

# - - -   _ S k i p I t e m . _ _ i n i t _ _   - - -

    def __init__ ( self, child, nLevels ):
        """Constructor for _SkipItem"""
        self.child  =   child
        self.links  =   [None]*nLevels

# - - - - -   c l a s s   _ S k i p L i s t I t e r a t o r   - - - - -

class _SkipListIterator:
    """Represents an active iterator over a SkipList object.

      Exports:
        _SkipListIterator ( skipItem ):
          [ skipItem is a _SkipItem ->
              return a new iterator whose next item is skipItem,
              or which is at end of list if skipItem's forward
              link points to itself ]
        .skipItem:
          [ if self is exhausted ->
              a terminator _SkipItem
            else ->
              a _SkipItem containing the value that will be returned
              next time ]
        .__iter__(self):    [ returns self ]
        .next():
          [ if self.skipItem's level-0 link is None ->
              raise ValueError
            else if self.skipItem.links[0] == self.skipItem ->
              raise StopIteration
            else ->
              self.skipItem  :=  self.skipItem.links[0]
              return self.skipItem.child ]  # *Before* advancing!
    """

# - - -   _ S k i p L i s t I t e r a t o r . _ _ i n i t _ _   - - -

    def __init__ ( self, skipItem ):
        """Constructor for _SkipListIterator"""
        self.skipItem  =  skipItem

# - - -   _ S k i p L i s t I t e r a t o r . n e x t   - - -

    def next ( self ):
        """Return the next child item and advance"""
        if  self.skipItem.links[0] is None:
            raise ValueError, "Iterator points to a deleted item."
        elif  self.skipItem.links[0] is self.skipItem:
            raise StopIteration
        else:
            result  =  self.skipItem.child
            self.skipItem  =  self.skipItem.links[0]
            return result
# - - -   _ S k i p L i s t I t e r a t o r . _ _ i t e r _ _   - - -

    def __iter__ ( self ):
        """Returns the iterator itself."""
        return self
# - - - - -   c l a s s   S k i p L i s t   - - - - -

class SkipList:
    """Container class for ordered sets.

      Exports:
        SkipList ( keyFun=None, cmpFun=None, allowDups=0,
                   count=1000000 ):
          [ (keyFun is a function that returns the key for a
             given child object) and
            (cmpFun is a function that compares two keys, using
             the usual Python convention for the cmp() function,
             or None use the built-in cmp() function) and
            (allowDups is 0 to refuse duplicate entries or 1 to
             allow them) and
            (count is a worst-case maximum element count) ->
              return a new, empty SkipList instance with those
              properties ]
        .insert(c):
          [ c is a child object ->
              if ((self contains an object whose key equals the key
                   of e) and (self.allowDups is false)) ->
                raise KeyError
              else ->
                self  :=  self with e added as a new child object ]
        .delete(k):
          [ k is in the key domain ->
              if self contains any child objects with keys equal to k ->
                self  :=  self with the first-inserted such child object
                          deleted
                return that child object
              else ->
                return None ]
        .match(k):
          [ k is in the key domain ->
              if self contains any child objects whose keys equal k ->
                return the first such child object
              else -> raise KeyError ]
        .find(k):
          [ k is in the key domain ->
              if self contains any child objects whose keys are >= k ->
                return an iterator that will iterate over all
                child objects whose keys are >= k, in order ]
        .__len__(self):
          [ return the number of child objects in self ]
        .__iter__(self):
          [ return an iterator that will iterate over all the
            child objects in self in order ]
        .__contains__(self, k):
          [ if self contains any child objects whose keys equal k ->
              return 1
            else -> return 0 ]
        .__delitem__(self, k):      [ same as self.delete(k) ]
        .__getitem__(self, k):      [ same as self.match(k) ]
        .nSearches:  [INVARIANT: Number of searches performed ]
        .nCompares:  [INVARIANT: Number of child pairs compared ]
    """
#--
# Manifest constants
#--
    NEW_LEVEL_PROBABILITY   = 0.25  # The `p' of Pugh's article
#================================================================
# State and invariants
#----------------------------------------------------------------
# .keyFun:       [ as passed to constructor, read-only ]
# .cmpFun:       [ as passed to constructor, read-only ]
# .allowDups:    [ as passed to constructor, read-only ]
# .__maxLevels:
#   [ 1 + ceiling ( log (base 4) of count argument to constructor ) ]
# .__nLevels:
#   [ number of levels currently in use ]
#   INVARIANT: 1 <= self.__nLevels <= self.__maxLevels ]
# .__heads:
#   [ list of head pointers to each level ]
#   INVARIANT: self.__heads.links[0] is the head of a linked list
#   of _SkipItem objects, terminated by a link to self.__terminator,
#   and whose members contain all the child objects currently in
#   self, such that for any two adjacent objects (Xi, Xj),
#   children-are-ordered ( Xi, Xj ) is true.
#
#   INVARIANT: For i in [0,self.__maxLevels), the list rooted in
#   heads.links[i] is a linked list of _SkipItem objects,
#   terminated by a link to self.terminator, and containing
#   a subset of the linked list in heads.links[i-1] in the same order.
# .__terminator:    [ terminator for all linked lists ]
#   INVARIANT: self.terminator is a _SkipItem object with
#   self.__maxLevels forward links all pointing to itself
# .__nItems:        [ INVARIANT: number of child items in self ]
#--
# - - -   S k i p L i s t . _ _ i n i t _ _   - - -

    def __init__ ( self, keyFun=None, cmpFun=None, allowDups=0,
                   count=1000000 ):
        """Constructor for SkipList"""

        #-- 1 --
        self.keyFun     =  keyFun
        self.cmpFun     =  cmpFun
        self.allowDups  =  allowDups
        self.nSearches  =  0
        self.nCompares  =  0
        self.__nLevels  =  1
        self.__nItems   =  0
        #-- 2 --
        # [ self.__maxLevels  :=  (number of bits required to
        #       represent count, rounded to the next even number)/2+1 ]
        self.__maxLevels  =  self.__estimateLevels ( count )
        #-- 3 --
        # [ self.__terminator  :=  a new _SkipItem object whose
        #       links all point to itself
        #   self.__heads  :=  a new _SkipItem object whose links
        #       all point to that new terminator _SkipItem object ]
        self.__terminator  =  _SkipItem ( None, self.__maxLevels )
        self.__heads       =  _SkipItem ( None, self.__maxLevels )
        for i in xrange ( self.__maxLevels ):
            self.__terminator.links[i]  =  self.__terminator
            self.__heads.links[i]  =  self.__terminator
# - - -   S k i p L i s t . _ _ e s t i m a t e L e v e l s   - - -

    def __estimateLevels ( self, n ):
        """Estimate how many levels of list we need for n child objects.

          [ n is a positive integer ->
              return ceiling(log base 4(n)) + 1 ]
        """

        #-- 1 --
        result  =  1

        #-- 2 --
        # [ result  +:=  k, where k is the the number of bits required
        #       to represent n, rounded to the next higher even number ]
        while  n > 0:
            result  +=  1
            n  >>=  2

        #-- 3 --
        return result
# - - -   S k i p L i s t . i n s e r t   - - -

    def insert ( self, child ):
        """Insert a new child element into the skip list."""
        #-- 1 --
        # [ key  :=  key-of ( child ) ]
        key  =  self.__keyOf ( child )
        #-- 2 --
        # [ cutList  :=  insertion-cut-list ( key ) ]
        cutList  =  self.__insertCutList ( key )

        #-- 3 -
        # [ prevItem  :=  first item from cutList
        #   nextItem  :=  successor at level 0 of first item from
        #                 cutList ]
        prevItem  =  cutList[0]
        nextItem  =  prevItem.links[0]
        #-- 4 --
        # [ if (not self.allowDups) and
        #   (nextItem is not self.terminator) and
        #   (cmp(key-of(nextItem.child, key)) == 0 ) ->
        #       raise ValueError
        #   else -> I ]
        if ( ( not self.allowDups ) and
             ( nextItem is not self.__terminator ) and
             ( self.__compareItemKey ( nextItem, key ) == 0 ) ):
            raise ValueError
        #-- 5 --
        # [ if cutList is insertion-cut-list ( key ) ->
        #     self  :=  self with a new _SkipItem containing (child)
        #               inserted after the items pointed at by the
        #               the first n elements of cutList, where
        #               n is in [1,self.__maxLevels] ]
        self.__insertItem ( child, cutList )
        #-- 6 --
        self.__nItems  =  self.__nItems + 1
# - - -   S k i p L i s t . _ _ k e y O f   - - -

    def __keyOf ( self, child ):
        """Return the child's key.

          [ child is in the child domain of self ->
              return key-of ( child ) ]
        """
        if self.keyFun:
            return self.keyFun ( child )
        else:
            return child
# - - -   S k i p L i s t . _ _ i n s e r t C u t L i s t   - - -

    def __insertCutList ( self, key ):
        """Form the insertion cut list.

          [ key is in self's key domain ->
              return insertion-cut-list(key) ]
        """    
        #-- 1 --
        # [ result      :=  a list of size self.__maxLevels such that
        #                   each element is self.__heads
        #   searchItem  :=  self.__heads ]
        result      =  [self.__heads] * self.__maxLevels
        searchItem  =  self.__heads
        #-- 2 --
        # [ if insertion-precedes ( searchItem, key ) ->
        #     result      :=  result modified so that for I in
        #                     [0,self.nLevels), result[I] is
        #                     insertion-point(I, key)
        #     searchItem  :=  <anything> ]
        for level in xrange ( self.__nLevels - 1, -1, -1 ):
            #-- 2 body --
            # [ if insertion-precedes(searchItem, key) ->
            #     searchItem     :=  insertion-point-after(level,
            #                        key, searchItem)
            #     result[level]  :=  <same as previous line> ]
            searchItem     =  self.__insertPoint ( searchItem, level, key )
            result[level]  =  searchItem
        #-- 3 --
        self.nSearches  =  self.nSearches + 1       # Count as a search
        return result
# - - -   S k i p L i s t . _ _ i n s e r t P o i n t   - - -

    def __insertPoint ( self, searchItem, level, key ):
        """Find the insertion point at a given level.

          [ insertion-precedes(searchItem, key) ->
              return insertion-point-after ( level, key, searchItem) ]
        """
        #-- 1 --
        # [ prevItem  :=  searchItem
        #   nextItem  :=  successor of searchItem in (level)th list ]
        prevItem  =  searchItem
        nextItem  =  searchItem.links[level]
        #-- 2 --
        # [ if nextItem is not self.__heads ->
        #     if not insertion-precedes(nextItem, key) -> I
        #     else ->
        #       prevItem  :=  last item E at or after nextItem
        #                     in the (level)th list such that
        #                     insertion-precedes(E, key) is true
        #       nextItem  :=  <anything> ]
        while self.__insertionPrecedes ( nextItem, key ):
            #-- 2 body --
            # [ prevItem  :=  nextItem
            #   nextItem  :=  the succesor of nextItem in the
            #                 (level)th list ]
            prevItem  =  nextItem
            nextItem  =  nextItem.links[level]
        #-- 3 --
        return prevItem
# - - -   S k i p L i s t . _ _ i n s e r t i o n P r e c e d e s   - - -


    def __insertionPrecedes ( self, skipItem, key ):
        """Does this _SkipItem precede this key for insertion?

          [ skipItem is not self.__heads ->
              return keys-are-ordered ( key-of ( skipItem's child ),
                                        key ) ]
        """
        #-- 1 --
        if skipItem is self.__terminator:
            return 0
        #-- 2 --
        # [ comparison  :=  cmp ( key-of ( skipItem's child ), key ) ]
        comparison  =  self.__compareItemKey ( skipItem, key )
        #-- 3 --
        #
        # Note: if duplicates are disallowed, and there is an item that
        # duplicates (target), we want to point before the duplicate
        # item so that the .insert() method will see it and fail.
        # If duplicates are allowed, though, we want to point after
        # all matching items so that the list order will reflect
        # the insertion order.
        #
        # [ if self.allowDups ->
        #     if comparison <= 0  ->  return 1
        #     else ->  return 0
        #   else ->
        #     if comparison < 0 ->  return 1
        #     else ->  return 0 ]
        if self.allowDups:
            return ( comparison <= 0 )
        else:
            return ( comparison < 0 )
# - - -   S k i p L i s t . _ _ c o m p a r e I t e m K e y   - - -

    def __compareItemKey ( self, skipItem, keyB ):
        """Compare the key from a _SkipItem to a key in the key domain.

          [ return cmp ( key-of ( skipItem's child ), keyB ) ]
        """
        #-- 1 --
        # [ keyA  :=  key-of ( skipItem's child ) ]
        keyA  =  self.__keyOf ( skipItem.child )
        #-- 2 --
        self.nCompares  =  self.nCompares + 1
        return cmp ( keyA, keyB )
# - - -   S k i p L i s t . _ _ i n s e r t I t e m   - - -


    def __insertItem ( self, child, cutList ):
        """
          [ cutList is insertion-cut-list(key-of(child)) ->
              self  :=  self with a new _SkipItem, with child=(child),
                        inserted after the items pointed at by the
                        first n levels of cutList, where n is in the
                        range [1,self.__maxLevels] ]
        """
        #-- 1 --
        # [ levels          :=  a random integer in [1,self.__maxLevels]
        #   self.__nLevels  :=  max ( self.__nLevels,
        #                             that random integer ) ]
        levels  =  self.__pickLevel ( )
        #-- 2 --
        # [ newItem  :=  a new _SkipItem with child=(child) and
        #                (levels) forward links all set to None ]
        newItem  =  _SkipItem ( child, levels )

        #-- 3 --
        # [ (cutList is insertion-cut-list(key-of(child))) and
        #   (newItem is a _SkipItem with at least (levels) links) ->
        #     self  :=  self with newItem linked into the first (levels)
        #               lists, just after the element pointed at by the
        #               corresponding element of cutList ]
        self.__insertRelink ( levels, cutList, newItem )
# - - -   S k i p L i s t . _ _ p i c k L e v e l   - - -

    def __pickLevel ( self ):
        """Into how many levels should an insertion be linked?

          [ self.__nLevels  :=  max ( self.__nLevels,
                a randomly chosen integer in [1,self.__maxLevels] )
            return that same integer ]
        """
        #-- 1 --
        result  =  1
        maxNewLevel  =  min ( self.__nLevels + 1, self.__maxLevels )
        #-- 2 --
        # [ maxNewLevel >= result  ->
        #     result  :=  a randomly chosen integer in the range
        #                 [result,maxNewLevel] ]
        while ( ( random.random() <= self.NEW_LEVEL_PROBABILITY ) and
                ( result < maxNewLevel ) ):
            result  =  result + 1
        #-- 3 --
        self.__nLevels  =  max ( self.__nLevels, result )

        #-- 4 --
        return result
# - - -   S k i p L i s t . _ _ i n s e r t R e l i n k   - - -

    def __insertRelink ( self, levels, cutList, newItem ):
        """Insert the new _SkipItem into all its linked lists.

          [ (cutList is insertion-cut-list(key-of(child))) and
            (newItem is a _SkipItem with child=(child) and
            at least (levels) links) ->
              self  :=  self with newItem linked into the first (levels)
                        lists, just after the element pointed at by the
                        corresponding element of cutList ]
        """

        #-- 1 --
        for i in xrange(levels):

            #-- 1 loop --
            # [ i is an integer in [0,levels) ->
            #     newItem.links[i]     :=  cutList[i].links[i]
            #     cutList[i].links[i]  :=  newItem ]

            #-- 1.1 --
            # [ i is an integer in [0,levels) ->
            #     prevItem  :=  the item pointed at by cutList[i]
            #     succItem  :=  the (i)th link from the item
            #                   pointed at by cutList[i] ]
            prevItem  =  cutList[i]
            succItem  =  prevItem.links[i]

            #-- 1.2 --
            # [ i is an integer in [0,levels) ->
            #     newItem   :=  newItem with its (i)th link
            #                   pointing to succItem
            #     prevItem  :=  prevItem with its (i)th link
            #                   pointing to newItem ]
            newItem.links[i]   =  succItem
            prevItem.links[i]  =  newItem
# - - -   S k i p L i s t . d e l e t e   - - -

    def delete ( self, key ):
        """Delete the first or only child with a given key value.
        """
        #-- 1 --
        # [ cutList   :=  search-cut-list ( key )
        #   prevItem  :=  first element of search-cut-list ( key )
        #   nextItem  :=  successor to first element of
        #                 search-cut-list ( key ) ]
        cutList   =  self.__searchCutList ( key )
        prevItem  =  cutList[0]
        nextItem  =  prevItem.links[0]
        #-- 2 --
        # [ if (nextItem is self.__terminator) or
        #   ( cmp ( key-of ( nextItem's child ), key ) ) > 0 ) ->
        #     return None
        #   else -> I ]
        if ( ( nextItem is self.__terminator ) or
             ( self.__compareItemKey ( nextItem, key ) > 0 ) ):
            return None
        #-- 3 --
        # [ self  :=  self modified so that for all I in
        #             [0,self.__nLevels), if the skipItem pointed to by
        #             cutList[I] has an (I)th link that points to
        #             nextItem, make that link point where nextItem's
        #             (I)th link points ]
        for i in xrange(self.__nLevels):
            #-- 3 body --
            # [ if the _SkipItem pointed to by cutList[i] has an
            #   (i)th link that points to nextItem ->
            #     that link is made to point where nextItem's (i)th
            #     link points ]
            prevItem  =  cutList[i]
            if  prevItem.links[i] is nextItem:
                prevItem.links[i]  =  nextItem.links[i]
        #-- 4 --
        self.__nItems      =  self.__nItems - 1
        nextItem.links[0]  =  None
        return nextItem.child
# - - -   S k i p L i s t . _ _ s e a r c h C u t L i s t   - - -

    def __searchCutList ( self, key ):
        """Find predecessors of the item with a given key.

          [ key is in self's key domain ->
              return search-cut-list ( key ) ]
        """
        #-- 1 --
        # [ result      :=  a list of size self.__maxLevels such that
        #                   each element is self.__heads
        #   searchItem  :=  self.__heads ]
        result      =  [self.__heads] * self.__maxLevels
        searchItem  =  self.__heads
        #-- 2 --
        # [ if search-precedes ( searchItem, key ) ->
        #     result      :=  result modified so that for I in
        #                     [0,self.__nLevels),
        #                     result[I]  := search-point(I, key)
        #     searchItem  :=  <anything> ]
        for i in xrange ( self.__nLevels-1, -1, -1 ):
            #-- 2 body --
            # [ if search-precedes ( searchItem, key ) ->
            #     result[i]   :=  search-point-after(i, key, searchItem)
            #     searchItem  :=  <same as previous line> ]
            searchItem  =  self.__searchPoint ( searchItem, i, key )
            result[i]   =  searchItem
        #-- 3 --
        self.nSearches  =  self.nSearches + 1
        return result
# - - -   S k i p L i s t . _ _ s e a r c h P o i n t   - - -

    def __searchPoint ( self, searchItem, level, key ):
        """Search one level of the skip list for a given key.

          [ ( level is in [0,self.__maxLevels ) ) and
            ( search-precedes ( searchItem, key ) ) ->
                return search-point-after ( level, key,
                searchItem ) ]
        """
        #-- 1 --
        # [ prevItem  :=  searchItem
        #   nextItem  :=  successor of searchItem in (level)th list ]
        prevItem  =  searchItem
        nextItem  =  searchItem.links[level]
        #-- 2 --
        # [ if nextItem is not self.__heads ->
        #     if search-precedes ( nextItem, key ) ->
        #       prevItem  :=  last item E in nth-list(nextItem, level)
        #                     such that search-precedes(E, key) is true
        #       nextItem  :=  <anything>
        #     else -> I ]
        while self.__searchPrecedes ( nextItem, key ):
            prevItem  =  nextItem
            nextItem  =  nextItem.links[level]
        #-- 3 --
        return prevItem
# - - -   S k i p L i s t . _ _ s e a r c h P r e c e d e s   - - -

    def __searchPrecedes ( self, skipItem, key ):
        """Does this item precede the item with a given key?

          [ ( skipItem is a _SkipItem ) and
            ( key is in self's key domain) ->
                if search-precedes ( skipItem, key ) ->
                  return 1
                else ->
                  return 0 ]
        """
        #-- 1 --
        if  skipItem is self.__terminator:
            return 0

        #-- 2 --
        # [ if cmp ( key-of(skipItem's child), key ) < 0 ->
        #     return 1
        #   else ->
        #     return 0 ]
        if  self.__compareItemKey ( skipItem, key ) < 0:
            return 1
        else:
            return 0
# - - -   S k i p L i s t . m a t c h   - - -

    def match ( self, key ): 
        """Return the first or only child with the given key.
        """
        #-- 1 --
        # [ searchItem  :=  successor of search-point ( 0, key ) ]
        prevItem    =  self.__searchCutItem(key)
        searchItem  =  prevItem.links[0]
        #-- 2 --
        # [ (searchItem is a _SkipItem in self) ->
        #     if (searchItem is not self.__terminator) and
        #     ( cmp ( key-of (searchItem's child), key ) ) == 0 )  ->
        #       return searchItem's child
        #     else ->
        #       raise KeyError ]
        if ( ( searchItem is not self.__terminator ) and
             ( self.__compareItemKey ( searchItem, key ) == 0 ) ):
            return searchItem.child
        else:
            raise KeyError, "Key not found: %s" % key
# - - -   S k i p L i s t . _ _ s e a r c h C u t I t e m   - - -

    def __searchCutItem ( self, key ):
        """Find the level-0 predecessor of the given key.

          [ key is in self's key domain ->
              return search-point(0, key).link[0] ]
        """

        #-- 1 --
        # [ searchItem  :=  self.__heads ]
        searchItem  =  self.__heads

        #-- 2 --
        # [ if search-precedes ( searchItem, key ) ->
        #     searchItem  :=  search-point ( 0, key ) ]
        for i in xrange ( self.__nLevels-1, -1, -1 ):
            #-- 2 body --
            # [ if search-precedes ( searchItem, key ) ->
            #     searchItem  :=  search-point-after(i, key, searchItem) ]
            searchItem  =  self.__searchPoint ( searchItem, i, key )

        #-- 3 --
        self.nSearches  =  self.nSearches + 1
        return searchItem
# - - -   S k i p L i s t . f i n d   - - -

    def find ( self, key ):
        """Return an iterator starting at a given position
        """
        #-- 1 --
        # [ searchItem  :=  search-point ( 0, key ).links[0] ]
        prevItem    =  self.__searchCutItem ( key )
        searchItem  =  prevItem.links[0]
        #-- 2 --
        return _SkipListIterator ( searchItem )
# - - -   S k i p L i s t . f i r s t   - - -
    def first(self):
        if self.__nItems == 0:
            raise KeyError, "skip list is empty"
        return self.__heads.links[0].child
    
# - - -   S k i p L i s t . _ _ l e n _ _   - - -

    def __len__ ( self ):
        """Returns the number of child elements."""
        return self.__nItems
# - - -   S k i p L i s t . _ _ i t e r _ _   - - -

    def __iter__ ( self ):
        """Iterator for the entire list"""
        return _SkipListIterator ( self.__heads.links[0] )
# - - -   S k i p L i s t . _ _ c o n t a i n s _ _   - - -

    def __contains__ ( self, key ):
        """Does self contain the given key?"""
        #-- 1 --
        try:
            child  =  self.match ( key )
            return 1
        except KeyError:
            return 0
# - - -   S k i p L i s t . _ _ d e l i t e m _ _   - - -

    def __delitem__ ( self, key ):
        """Delete the first or only item with a given key."""
        self.delete ( key )
# - - -   S k i p L i s t . _ _ g e t i t e m _ _   - - -

    def __getitem__ ( self, key ):
        """Get the first or only item with a given key."""
        return self.match ( key )

import lib.jlist as jlist
import json
import operator

def jpack(*args):

    """
    .. function:: jpack(args...) -> jpack

    Converts multiple input arguments into a single string. Jpacks preserve the types
    of their inputs and are based on JSON encoding. Single values are represented as
    themselves where possible.

    Examples:

    >>> sql("select jpack('a')")
    jpack('a')
    ----------
    a

    >>> sql("select jpack('a','b',3)")
    jpack('a','b',3)
    ----------------
    ["a","b",3]

    >>> sql("select jpack('a', jpack('b',3))")
    jpack('a', jpack('b',3))
    ------------------------
    ["a",["b",3]]

    """

    return jlist.toj(jlist.elemfromj(*args))

jpack.registered=True

def jfilterempty(*args):
    """
    .. function:: jfilterempty(jpacks.) -> jpack

    Removes from input jpacks all empty elements.

    Examples:

    >>> sql("select jfilterempty('a', '', '[]')")
    jfilterempty('a', '', '[]')
    ---------------------------
    a

    >>> sql("select jfilterempty('a','[null]',3)")
    jfilterempty('a','[null]',3)
    ----------------------------
    ["a",3]

    >>> sql("select jfilterempty('[3]', jpack('b', ''))")
    jfilterempty('[3]', jpack('b', ''))
    -----------------------------------
    [3,"b"]

    """

    return jlist.toj([x for x in jlist.fromj(*args) if x!='' and x!=[] and x!=None])

jfilterempty.registered=True

def j2t(*args):

    """
    .. function:: j2t(jpack) -> tabpack

    Converts multiple input jpacks to a tab separated pack (tab separated values). If tab characters are found in
    the source jpack

    Examples:

    >>> sql("select j2t('[1,2,3]')") # doctest: +NORMALIZE_WHITESPACE
    j2t('[1,2,3]')
    --------------
    1        2        3

    >>> sql("select j2t('[1,2,3]','a')") # doctest: +NORMALIZE_WHITESPACE
    j2t('[1,2,3]','a')
    ------------------
    1        2        3        a

    >>> sql("select j2t('a', 'b')") # doctest: +NORMALIZE_WHITESPACE
    j2t('a', 'b')
    -------------
    a        b

    """

    return '\t'.join([ str(x).replace('\t', '    ') for x in jlist.fromj(*args) ])

j2t.registered=True

def t2j(*args):

    """
    .. function:: t2j(tabpack) -> jpack

    Converts a tab separated pack to a jpack.

    Examples:

    >>> sql("select t2j(j2t('[1,2,3]'))") # doctest: +NORMALIZE_WHITESPACE
    t2j(j2t('[1,2,3]'))
    -------------------
    ["1","2","3"]

    """
    
    fj=[]
    for t in args:
        fj+=t.split('\t')

    return jlist.toj(fj)

t2j.registered=True

def jmerge(*args):

    """
    .. function:: jmerge(jpacks) -> jpack

    Merges multiple jpacks into one jpack.

    Examples:

    >>> sql("select jmerge('[1,2,3]', '[1,2,3]', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jmerge('[1,2,3]', '[1,2,3]', 'a', 3 )
    -------------------------------------
    [1,2,3,1,2,3,"a",3]

    """

    return jlist.toj( jlist.fromj(*args) )

jmerge.registered=True

def jset(*args):

    """
    .. function:: jset(jpacks) -> jpack

    Returns a set representation of a jpack, unifying duplicate items.

    Examples:

    >>> sql("select jset('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jset('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )
    ----------------------------------------
    [1,2,3,"a","b"]

    """

    return jlist.toj(sorted(set( jlist.fromj(*args) )))

jset.registered=True

def jsort(*args):

    """
    .. function:: jsort(jpacks) -> jpack

    Sorts the input jpacks.

    Examples:

    >>> sql("select jsort('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )") # doctest: +NORMALIZE_WHITESPACE
    jsort('[1,2,3]', '[1,2,3]', 'b', 'a', 3 )
    -----------------------------------------
    [1,1,2,2,3,3,3,"a","b"]

    """

    return jlist.toj(sorted( jlist.fromj(*args) ))

jsort.registered=True

def jsplitv(*args):

    """
    .. function:: jsplitv(jpacks) -> [C1]

    Splits vertically a jpack.

    Examples:

    >>> sql("select jsplitv(jmerge('[1,2,3]', '[1,2,3]', 'b', 'a', 3 ))") # doctest: +NORMALIZE_WHITESPACE
    C1
    --
    1
    2
    3
    1
    2
    3
    b
    a
    3

    """

    yield ('C1', )

    for j1 in jlist.fromj(*args):
        yield [jlist.toj(j1)]

jsplitv.registered=True

def jsplit(*args):

    """
    .. function:: jsplit(jpacks) -> [C1, C2, ...]

    Splits horizontally a jpack.

    Examples:

    >>> sql("select jsplit('[1,2,3]', '[3,4,5]')") # doctest: +NORMALIZE_WHITESPACE
    C1 | C2 | C3 | C4 | C5 | C6
    ---------------------------
    1  | 2  | 3  | 3  | 4  | 5

    """

    fj=[jlist.toj(x) for x in jlist.fromj(*args)]

    if fj==[]:
        yield ('C1',)
            
    yield tuple( ['C'+str(x) for x in xrange(1,len(fj)+1)] )
    yield fj

jsplit.registered=True

def jflatten(*args):

    """
    .. function:: jflattten(jpacks) -> jpack

    Flattens all nested sub-jpacks.

    Examples:

    >>> sql(''' select jflatten('1', '[2]') ''') # doctest: +NORMALIZE_WHITESPACE
    jflatten('1', '[2]')
    --------------------
    ["1",2]

    >>> sql(''' select jflatten('[["word1", 1], ["word2", 1], [["word3", 2], ["word4", 2]], 3]') ''') # doctest: +NORMALIZE_WHITESPACE
    jflatten('[["word1", 1], ["word2", 1], [["word3", 2], ["word4", 2]], 3]')
    -------------------------------------------------------------------------
    ["word1",1,"word2",1,"word3",2,"word4",2,3]

    """

    return jlist.toj( jlist.flatten( jlist.elemfromj(*args) ))

jflatten.registered=True

def jmergeregexp(*args):

    """
    .. function:: jmergeregexp(jpacks) -> jpack

    Flattens all nested sub-jpacks.

    Examples:

    >>> sql(''' select jmergeregexp('["abc", "def"]') ''') # doctest: +NORMALIZE_WHITESPACE
    jmergeregexp('["abc", "def"]')
    ------------------------------
    (?:abc)|(?:def)

    """

    return '|'.join('(?:'+x+')' for x in jlist.fromj(*args))

jmergeregexp.registered=True

def jdictkeys(*args):

    """
    .. function:: jdictkeys(jdict) -> jpack

    Returns a jpack of the keys of input jdict

    Examples:

    >>> sql(''' select jdictkeys('{"k1":1,"k2":2}', '{"k1":1,"k3":2}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictkeys('{"k1":1,"k2":2}', '{"k1":1,"k3":2}')
    -----------------------------------------------
    ["k3","k2","k1"]

    >>> sql(''' select jdictkeys('{"k1":1,"k2":2}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictkeys('{"k1":1,"k2":2}')
    ----------------------------
    ["k2","k1"]
    >>> sql(''' select jdictkeys('test') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictkeys('test')
    -----------------
    []
    >>> sql(''' select jdictkeys(1) ''') # doctest: +NORMALIZE_WHITESPACE
    jdictkeys(1)
    ------------
    []

    """
    
    if len(args)==1:
        if type(args[0]) in (int,float) or args[0][0]!='{' or args[0][-1]!='}':
            keys=[]
        else:
            keys=[x for x in json.loads(args[0]).iterkeys()]
    else:
        keys=[]
        for i in args:
            if i[0]=='{' and i[-1]=='}':
                keys+=[x for x in json.loads(i).iterkeys()]
        keys=list(set(keys))
    return jlist.toj( keys )

jdictkeys.registered=True

def jdictvals(*args):

    """
    .. function:: jdictvals(jdict, [key1, key2,..]) -> jpack

    If only the first argument (jdict) is provided, it returns a jpack of the values of input jdict (sorted by the jdict keys).

    If key values are also provided, it returns only the keys that have been provided.

    Examples:

    >>> sql(''' select jdictvals('{"k1":1,"k2":2}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals('{"k1":1,"k2":2}')
    ----------------------------
    [1,2]

    >>> sql(''' select jdictvals('{"k1":1,"k2":2, "k3":3}', 'k3', 'k1', 'k4') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals('{"k1":1,"k2":2, "k3":3}', 'k3', 'k1', 'k4')
    ------------------------------------------------------
    [3,1,null]
    >>> sql(''' select jdictvals('{"k1":1}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals('{"k1":1}')
    ---------------------
    1
    >>> sql(''' select jdictvals('{"k1":1}') ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals('{"k1":1}')
    ---------------------
    1
    >>> sql(''' select jdictvals(1) ''') # doctest: +NORMALIZE_WHITESPACE
    jdictvals(1)
    ------------
    1

    """

    if type(args[0]) in (int,float) or args[0][0]!='{' or args[0][-1]!='}':
        return args[0]
    d=json.loads(args[0])
    if len(args)==1:
        d=d.items()
        d.sort(key=operator.itemgetter(1,0))
        vals=[x[1] for x in d]
    else:
        vals=[]
        for i in args[1:]:
            try:
                vals.append(d[i])
            except:
                vals.append(None)
        
    return jlist.toj( vals )

jdictvals.registered=True

def jdictsplit(*args):

    """
    .. function:: jdictvals(jdict, [key1, key2,..]) -> columns

    If only the first argument (jdict) is provided, it returns a row containing the values of input jdict (sorted by the jdict keys).

    If key values are also provided, it returns only the columns of which the keys have been provided.

    Examples:

    >>> sql(''' select jdictsplit('{"k1":1,"k2":2}') ''') # doctest: +NORMALIZE_WHITESPACE
    k1 | k2
    -------
    1  | 2

    >>> sql(''' select jdictsplit('{"k1":1,"k2":2, "k3":3}', 'k3', 'k1', 'k4') ''') # doctest: +NORMALIZE_WHITESPACE
    k3 | k1 | k4
    --------------
    3  | 1  | None

    """

    d=json.loads(args[0])
    if len(args)==1:
        d=d.items()
        d.sort(key=operator.itemgetter(1,0))
        yield tuple([x[0] for x in d])
        yield [x[1] for x in d]
    else:
        vals=[]
        yield tuple(args[1:])
        for i in args[1:]:
            try:
                vals.append(d[i])
            except:
                vals.append(None)
        yield vals

jdictsplit.registered=True


if not ('.' in __name__):
    """
    This is needed to be able to test the function, put it at the end of every
    new function you create
    """
    import sys
    import setpath
    from functions import *
    testfunction()
    if __name__ == "__main__":
        reload(sys)
        sys.setdefaultencoding('utf-8')
        import doctest
        doctest.testmod()
# Python script for turning sam-digested
# output of heegaard into twister format
# by Robert Haraway, 2016

def incidence_matrix(heeg_datum):
    half_incidence = heeg_datum[0]
    mat = {}
    for key in half_incidence:
        if key not in mat:
            mat[key] = {}
        neighbors = half_incidence[key]
        for neighbor in neighbors:
            if neighbor not in mat:
                mat[neighbor] = {}
            deg = half_incidence[key][neighbor]
            mat[key][neighbor] = deg
            mat[neighbor][key] = deg
    return mat

def right_numbered_CO(heeg_datum):
    inc = incidence_matrix(heeg_datum)
    CO = heeg_datum[2].copy()
    for key in CO:
        nbr_str = CO[key]
        incidences = inc[key]
        for neighbor in incidences:
            i = nbr_str.index(neighbor)
            before = nbr_str[0:i]
            after = nbr_str[i+1:]
            num_edges = incidences[neighbor]
            middle = num_edges * neighbor
            nbr_str = before + middle + after
        CO[key] = nbr_str
    return CO

def fold(op,id,l):
    # Higher-order function
    x = id
    s = list(l)
    while s != []:
        x = op(s.pop(),x)
    return x

def right_ordered_CO(heeg_datum):
    CO = right_numbered_CO(heeg_datum)
    lower_case_tuple = heeg_datum[1]
    lct = lower_case_tuple
    letters = list(CO)
    lc = list(filter(lambda x:x.islower(), letters))
    assert len(lc) == len(lct)
    lc.sort()
    for pair in zip(lc,lct):
        (key, i) = pair
        nbr_char_list = list(CO[key])
        ncl = nbr_char_list
        ncl.reverse()
        ch = ncl.pop()
        ncl = [ch] + ncl
        ncl = ncl[len(ncl)-i:] + ncl[:len(ncl)-i]
        cc = lambda x,y:x+y
        CO[key] = fold(cc,"",ncl)
    return CO

augmented_CO = right_ordered_CO

def attach_globs(heeg_datum):
    d = heeg_datum
    incd = incidence_matrix(d)
    ag = augmented_CO(d)
    return (d,ag,incd)

def ccw_flags(aCO,L):
    deg = len(aCO[L])
    positions = list(range(deg))
    if L.islower():
        positions.reverse()
    return list(map(lambda n: {'letter':L,'pos':n}, positions))

def cyclic_first(lb):
    ps = list(zip(lb[:-1],lb[1:]))
    if (False,True) in ps:
        return ps.index((False,True)) + 1
    else:
        return 0

def other_letter(aCO):
    return lambda flag: aCO[flag['letter']][flag['pos']]

def ccw_flags_between(aCO,L,nL):
    all_flags = ccw_flags(aCO,L)
    endpts = list(map(other_letter(aCO), all_flags))
    offset = cyclic_first(list(map(lambda x: x == nL, endpts)))
    N = len(all_flags)
    i = 0
    flags = []
    while endpts[(i+offset)%N] == nL and i < N:
        flags.append(all_flags[(i+offset)%N])
        i = i+1
    return flags

def flip(aCO,flag):
    L = flag['letter']
    nL = other_letter(aCO)(flag)
    Lflags = ccw_flags_between(aCO,L,nL)
    nLflags = ccw_flags_between(aCO,nL,L)
    nLflags.reverse()
    i = Lflags.index(flag)
    return nLflags[i]

def next_square(hdwg,flag):
    (hd,aCO,inc) = hdwg
    nflag = flip(aCO,flag)
    nL = nflag['letter']
    npos = nflag['pos']
    return {'letter':nL.swapcase(),'pos':npos}

def cycle(nxt,sq):
    cyc = [sq]
    n = nxt(sq)
    while n != sq:
        cyc.append(n)
        n = nxt(n)
    return cyc

def cyclically_equal(A,B):
    # Shiloach's algorithm.
    # See ``On the shape of mathematical arguments''
    # by A. J. M. van Gasteren, Springer Verlag, 1990.
    if len(A) != len(B):
        return False
    N = len(A)
    h,i,j = 0,0,0
    while h < N and i < N and j < N:
        if   A[(i+h)%N] == B[(j+h)%N]:
            h = h + 1
        elif A[(i+h)%N] >  B[(j+h)%N]:
            i = i + h + 1
            h = 0
        elif B[(j+h)%N] >  A[(i+h)%N]:
            j = j + h + 1
            h = 0
    return h >= N

def rev(word):
    temp = list(word)
    temp.reverse()
    return fold(lambda x,y:x+y,"",temp)

def word_cycle(hdwg,word):
    (hd,aCO,inc) = hdwg
    wds = [word,rev(word),word.swapcase(),rev(word).swapcase()]
    for wd in wds:
        L = wd[0:1]
        if L not in aCO:
            continue
        for pos in range(len(aCO[L])):
            start = {'letter':L,'pos':pos}
            nxt = lambda sq : next_square(hdwg,sq)
            cyc = cycle(nxt,start)
            A = list(map(lambda sq : sq['letter'], cyc))
            B = list(wd)
            if cyclically_equal(A,B):
                return cyc
    raise Exception(str(hdwg) + " " + word)

def twister_number_dict(heeg_datum_w_globs):
    hdwg = heeg_datum_w_globs
    (heeg_datum, aug_CO, inc) = hdwg
    deg = lambda letter:len(aug_CO[letter])
    UClets = list(filter(lambda x: x.isupper(), aug_CO))
    UClets.sort()
    dct = {}
    sq_num = 1 # We start the square numbering at 1,
               # not at 0, since this makes denoting
               # signs easier.
    for L in UClets:
        for pos in range(deg(L)):
            UCsq = (L,pos)
            lcsq = (L.swapcase(), pos)
            dct[UCsq] = sq_num
            dct[lcsq] = -sq_num
            sq_num = sq_num + 1
    return dct

def word_twister_nums(heeg_datum_w_globs, word, dct):
    # dct should be the result of
    # twister_number_dict(heeg_datum_w_globs).
    h = heeg_datum_w_globs
    cyc = word_cycle(h,word)
    n = len(cyc)
    i = 0
    tnums = []
    while i < n:
        sq = cyc[i]
        p = (sq['letter'], sq['pos'])
        tnums.append(dct[p])
        i = i + 1
    return (word,tnums)

def all_twister_nums(heeg_datum_w_globs, words):
    h = heeg_datum_w_globs
    dct = twister_number_dict(h)
    ws = []
    for word in words:
        ws.append(word_twister_nums(h,word,dct))
    wns = []
    for (word,tnums) in ws:
        wns.extend(tnums)
    ag = h[1]
    UClets = list(filter(lambda x:x.isupper(), list(ag)))
    gs = []
    deg = lambda x: len(ag[x])
    for L in UClets:
        i = 0
        tnums = []
        n = deg(L)
        while i < n:
            tn = dct[(L,i)]
            if tn in wns:
                tn = dct[(L.swapcase(),i)]
            tnums.append(tn)
            i = i + 1
        gs.append((L,tnums))
    return ws + gs

def tnum_string(n):
    # We now revert the numbering for the
    # square back, to start at 0.
    assert n != 0
    if n > 0:
        return ",+" + str(n-1)
    elif n < 0:
        return ",-" + str(-n-1)

def twister_line(word,tnums):
    start = "annulus," + word + "," + rev(word).swapcase()
    Ts = fold(lambda x,y: x + y, "", map(tnum_string, tnums))
    return start + Ts + "#\n"

def twister_string(heeg_datum,words):
    header = "# A Twister surface file\n"
    h = attach_globs(heeg_datum)
    curves = all_twister_nums(h,words)
    body = ""
    for (word,tnums) in curves:
        body = twister_line(word,tnums) + body
    return header + body

def heegaard_to_twister(digested):
    words = digested[0]
    heeg_datum = digested[1:]
    return twister_string(heeg_datum,words)

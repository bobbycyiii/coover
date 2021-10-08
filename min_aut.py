import re
import itertools

#### Code for finding shortlex minimal element under Aut(F(a, b)) orbit of a word.
#### Inverses of generators are represented by capital letters.

## Freely reduces w
def freely_reduce(w):
    reduction_occured = True
    while reduction_occured :
        reduction_occured = False
        for i in range(len(w) - 1) :
            if w[i] == w[i+1].swapcase() :
                reduction_occured = True
                w = w[:i] + w[i+2:]
                break
    return w


def min_word(w1, w2):
    return min((w1, w2), 
        key=lambda w: (len(w), tuple("abAB".index(c) for c in w)))


## Swaps a for b and A for B
def swapgens(w) :
    assert set(w).issubset(set("abAB"))
    return w.translate(w.maketrans("abAB","baBA"))


## Performs Whitehead automorphism of type 1:
## swap - if true swaps a for b and A for B
## ainverse - if true swaps a with A
## binverse - if true swaps b with B
def wh1(swap, ainverse, binverse, w) :
    if ainverse :
        w = w.translate(w.maketrans("aA","Aa"))
    if binverse :
        w = w.translate(w.maketrans("bB","Bb"))
    if swap :
        return swapgens(w)
    else :
        return w


## Applies whitehead automorphism of type 2 to word: returns (A, x)w.
## A - subset of the generators containing x
## x - a generator or inverse generator
## w - a word to apply the automorphism to
def wh2(A, x, w) :
	nw = ''
	for y in w :
		if y in A :
			if y.swapcase() in A :
				nw += x.swapcase() + y + x
			else :
				if y != x and y != x.swapcase() :
					nw += y + x
				else :
					nw += y
		elif y.swapcase() in A :
			if y != x and y != x.swapcase() :
				nw += x.swapcase() + y
			else :
				nw += y
		else :
			nw += y
	return nw
		

## Tries all automorphisms of type 2 to w. If one such automorphism shortens the length, 
## then return this shorter word. If not, then returns w.
def find_shorter_word(w) :
    generators = ['a', 'b', 'A', 'B']
    Asubsets = [[], ['a'], ['A'], ['a', 'A']]
    Bsubsets = [[], ['b'], ['B'], ['b', 'B']]
    
    for gen in generators :

        if gen in ['a', 'A'] :
            subsets = [[gen] + Bsubset for Bsubset in Bsubsets]
        else :
            subsets = [[gen] + Asubset for Asubset in Asubsets]

        for subset in subsets :
            nw = freely_reduce(wh2(subset, gen, w))
			
            if len(nw) < len(w) :
                return nw
    return w


## Finds a shortest length word in the Aut(F(a, b)) orbit of w.
def shortest_word(w) :
    shorter = True
    while shorter :
        shorter = False
        ## Compute shorter word under automorphisms of type 2
        nw = find_shorter_word(w)
        ## If word length goes down, repeat loop with new word
        if len(nw) < len(w) :
            w = nw
            shorter = True
    return w				

	
## Finds the shortlex minimal word under Aut(F(a, b)) orbit.
def shortlex_min(word) :
    ## Checks if input word is over the generator a, b, A, B
    if not re.fullmatch('(a|b|A|B)*', word) :
        raise Value_error('Invalid input word!')

    generators = ['a', 'b', 'A', 'B']
    Asubsets = [[], ['a'], ['A'], ['a', 'A']]
    Bsubsets = [[], ['b'], ['B'], ['b', 'B']]

	## compute a shortest length word under the action of Aut(F(a, b))
    word = shortest_word(word)
	
    ws = [word]
    nws = [word]
	
	## Apply whitehead automorphisms of type 1 until no new words are produced
    nws_added = True
    while nws_added :
        nws_added = False
        nws1 = []
        
        ## Iterate through words to apply Whitehead automorphisms of type 2
        for w in nws :
			## Apply all possible Whitehead automorphisms of type 2 and add new shortest words to list
    
            for gen in generators :

                if gen in ['a', 'A'] :
                    subsets = [[gen] + Bsubset for Bsubset in Bsubsets]
                else :
                    subsets = [[gen] + Asubset for Asubset in Asubsets]
                    
                for subset in subsets :
                    nw = freely_reduce(wh2(subset, gen, w))
					
                    ## Check if word increased in size
                    if len(nw) == len(w) :
                        if nw not in ws :
                            ws += [nw]
                            nws1 += [nw]
                            
        if nws1 :
            nws_added = True
            
        nws = nws1
        
    minw = ws[0]
    
    for w in ws :
        wh1c = [list(i) for i in itertools.product([True, False], repeat=3)]
        ## Apply all Whitehead automorphisms of type 1 to w
        for c in wh1c :
            ## Check if any of the new words is shortlex smaller
            minw = min_word(wh1(c[0], c[1], c[2], w), minw)
    return minw


## If w = u^p for some u not a proper power, then returns u.
def root_word(w) :
    ## Find second occurence of first half of word w
    l = w[1:].find(w[:int(len(w)/2)]) + 1
    if l == 0 :
        return w
    elif w == w[:l]*int(len(w)/l) :
        return w[:l]
    else :
        return w


## First argument should be a word over a, b, A, B.
## Second (optional) argument should be True or False.
## Prints shortlex minimal element or input word under Aut(F(a, b)) orbit.
## If second argument is True, prints generator of shortlex
## minimal cyclic subgroup containing input word.
if __name__ == '__main__' :
    import sys
    word = sys.argv[1]
    if len(sys.argv) > 2:
        if sys.argv[2] == 'True' :
            print(root_word(shortlex_min(str(word))))
        else :
            print(shortlex_min(str(word)))
    else :
        print(shortlex_min(str(word)))

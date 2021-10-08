import csv
import sys
import relators_to_tri as rt
import dunfield
import min_aut
from pprint import pprint

hb = '../heegaard/berge_heegaard/heegaard_docker'

all_words = []
with open(sys.argv[1], 'r') as fp:
  for line in fp:
    rel = line.strip()
    if len(rel) > 0:
      all_words.append(rel)

realizable = {}
failed = {}

def syllable_len(w):
  if len(w) == 0:
    return 0
  prev = w[0]
  syllables = 1
  for c in w:
    if c != prev:
      syllables +=1
      prev = c
  return syllables

with open(sys.argv[2], 'w') as csv_file:
  writer = csv.writer(csv_file, delimiter=',')
  for r in all_words:
    print(f"================= {r} ==================")
    word = r.translate(r.maketrans("xyXY","abAB"))
    short_lex = min_aut.shortlex_min(word)  
    syl_len = syllable_len(short_lex)
    mfld = rt.relators_to_tri([short_lex], hb, clean_up=False, verbose=True)
    if mfld is not None:
      try:
        isosig = mfld.isometry_signature()
      except:
        isosig = mfld.triangulation_isosig()
      kind, name = dunfield.identify_with_bdy_from_isosig(isosig)
      realizable[r] = (r, short_lex, syl_len, name, kind, isosig)
      writer.writerow(realizable[r]) 
    else:
      failed[r] = (r, short_lex, syl_len, "failed", "failed", "failed")
      writer.writerow(failed[r]) 


import snappy as sp
import diagram_data as dd
import extraction as ext
import os

def relators_to_tri(relators, heegaard_bin, name=None,
                    clean_up=False, verbose=False):
  if not name:
    name = '_'.join(relators)

  datum, err = dd.get_diagram_data(relators, heegaard_bin)

  if err:
    print('Error getting diagram: {}\n    {}'.format(err, datum))

  sur_file = name + '.sur'

  with open(sur_file, 'w') as fp:
    fp.write(ext.heegaard_to_twister(datum))

  sur = sp.twister.Surface(sur_file)
  rels = datum[0] #TODO fix this convertion
  gens = list(set(''.join(rels).lower()))
  handles = '*'.join(gens + rels)
  manifold = sur.splitting('', handles)

  if verbose:
    print(manifold.identify())

  tri_file = name + '.tri'
  manifold.save(tri_file)

  if clean_up:
    os.remove(sur_file)
    os.remove(tri_file)

  return manifold

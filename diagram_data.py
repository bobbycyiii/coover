"""

diagram_data: A Python interface for Marc Culler's port of
John Berge's Heegaard program

Provides the function 'get_diagram_data' which currently
only prints out the text data of the presentation

"""

import io, re
from heegaard_tools import tty_capture

g_heegaard_bin = ['/home/sage/yarmola/Projects/heegaard/berge_heegaard/heegaard_docker']

def skip_returns(stream):
  try:
    line = stream.readline()
    while not line.rstrip():
      line = stream.readline()
      if not line:
        return None
    return line
  except:
    print("Error: bad file stream")
    return None

def get_diagram_info(relations, heegaard_bin, reduce=False):
  """

  >>> get_diagram_info(['aabbAbbaabbABAAABAbb', 'aabbaabbbaabbABAbbaabbbaabbaabbb'])
  >>> get_diagram_info(['bbaaccabc'])
  >>> get_diagram_info(['AABCab','ACCBcb'])

  """

  pres_name = ''
  cmds = ['k']
  for rel in relations:
    cmds += [rel, '\n']
    pres_name += rel + '|'
  pres_name = pres_name[:-1]
  cmds += ['\n']

  cmds += [pres_name, '\n']

  if reduce:
    # TODO Reduction seems unnecessary
    # r - We should reduce our presentation before getting the data
    # n - Do not form bandsums
    # n - Do not delete all primitive relators
    # n - Do not even delete small primitive relators
    # n - Do not turn on Micro_Printing
    cmds += ['r', 'n', 'n', 'n', 'n']
    # d - Run the diagram algorithm.
    # n - Do not review presentations (does not always appear)
    cmds += ['d', 'n', 'b', 'q', 'q']
  else:
    # d - Run the diagram algorithm. Heegaard should reduce on its own
    cmds += ['d', '\n']

  output_str, err = tty_capture(heegaard_bin, cmds)

  if err:
    print('Error running heegaard: {0}'.format(err))
    return None, err

  output = io.StringIO(output_str)

  line = ''
  # Get the presentation number
  pres_str = ''
  while "Data For Diagram" not in line:
    line = skip_returns(output)
    if not line:
      return None, "No diagram found"
    pres_str += line

  pres_num = re.match(r'\s+Data For Diagram (\d+) ', line)[1]
  pres_out = io.StringIO(pres_str)
  pres_line = ''
  if reduce:
    while "Presentation {} ".format(pres_num) not in pres_line:
      pres_line = skip_returns(pres_out)
  else:
    while "rewritten initial presentation is" not in pres_line:
      pres_line = skip_returns(pres_out)

  rels = []
  pres_line = skip_returns(pres_out)
  if pres_line[0] != ' ':
    pres_line = skip_returns(pres_out)
  while pres_line[0] == ' ':
    rels.append(pres_line.strip())
    pres_line = skip_returns(pres_out) 

  # Get the diagram
  edge_trigger = "The following table gives the number of edges joining each pair of vertices"
  while edge_trigger not in line:
    line = skip_returns(output)

  # Skip the next new line
  line = skip_returns(output)
  edge_table = line.rstrip() 

  # See if we get an message or we got something nice
  table_is_complete_trigger = "For each (X,x) pair"
  line = skip_returns(output)
  if table_is_complete_trigger not in line:
    print('Error table incomplete: {0}'.format(line))
    return {'relators': rels, 'edge_table': edge_table}, 'table incomplete'

  # Skip explanation
  num_edge_trigger = "at x the number shown in the following list"
  while num_edge_trigger not in line:
    line = skip_returns(output)

  # Get the number edges for first vertex (what exactly is this?)
  line = skip_returns(output)
  num_edges = line.rstrip()

  # See if we make it to clockwise order of vertices
  clockwise_trigger = "Vertices in the boundary of each face of the Heegaard diagram in clockwise order are"
  line = skip_returns(output)
  if clockwise_trigger not in line:
    print('Error no clockwise trigger: {0}'.format(line))
    return ({'relators': rels,
             'edge_table': edge_table,
             'num_edges': num_edges}, 'no clockwise trigger')

  # Get the vertices in clockwise order
  line = skip_returns(output)
  cw_order = line.rstrip()

  # Get infinite face cycle.
  line = skip_returns(output)
  infc = line.rstrip()
  infc = infc.replace("Note: Heegaard chose the cycle '",'')
  infinite_face_cycle = infc.replace("' to be the boundary of the 'infinite' face.",'')

  # Check that CO list is next
  co_list_trigger = "lists the vertices in the link of vertex v in counter-clockwise cyclic order"
  line = skip_returns(output)
  if co_list_trigger not in line:
    print('Error no colist trigger: {0}'.format(line))
    return ({'relators': rels,
             'edge_table': edge_table,
             'num_edges': num_edges,
             'clockwise_order': cw_order,
             'inf_face_cycle': infinite_face_cycle}, 'no colist trigger')

  # Get the CO list
  line = skip_returns(output)
  co_list = line.rstrip()

  return ({'relators': rels,
           'edge_table': edge_table,
           'num_edges': num_edges,
           'clockwise_order': cw_order,
           'inf_face_cycle': infinite_face_cycle,
           'co_list': co_list}, None)


def get_diagram_data(relations, heegaard_bin, reduce=False):
  heeg_info, err = get_diagram_info(relations, heegaard_bin, reduce)
  if err:
    print("Error with heergaard info: {}".format(err))
    return None, err

  edge_data = {}
  co_data = {}
  
  for edge_str in heeg_info['edge_table'].split(', '):
    # edge_str shoud look like: (A --> a2,B3,b3,C2)
    m = re.match(r'\(([a-zA-Z]+) --> (\S+)\)', edge_str)
    gen, edge_str = m[1], m[2]
    edges = {}

    for e in edge_str.split(','):
      m = re.match(r'([a-zA-Z]+)([0-9]+)', e)
      edges[m[1]] = int(m[2])

    edge_data[gen] = edges   

  for co in heeg_info['co_list'].split(', '):
    # co should look like: CO[A] = abCB
    m = re.match(r'CO\[([a-zA-Z]+)\] = ([a-zA-Z]+)', co)
    co_data[m[1]] = m[2]

  return [heeg_info['relators'], edge_data, eval(heeg_info['num_edges']), co_data], None


__all__ = ["get_diagram_data"]

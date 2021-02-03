import random
import fileinput as fi
from inspect import stack
import logging
from contextlib import closing
import graph_tool.all as gt
import matplotlib

class Graken:
  from .search import search_bfs
  def __init__(self):
    logging.debug(str(self.__class__.__name__)+' -> '+str(stack()[0][3])+'() in '+str(__file__))
    logging.info('OpenMP enabled '+str(gt.openmp_enabled())+' with '+str(gt.openmp_get_num_threads())+' Threads')
    self.graph = gt.Graph()
    self.graph.set_directed(True)
    self.nodes = {}
    self.parallel_options = []
    self.graph.vertex_properties['name'] = self.graph.new_vp('string')
    self.graph.vertex_properties['parallel'] = self.graph.new_vp('vector<string>')
    self.graph.edge_properties['distance'] = self.graph.new_ep('double')
    self.graph.edge_properties['name'] = self.graph.new_ep('string')
    self.graph.edge_properties['trigger'] = self.graph.new_ep('string')
    self.graph.edge_properties['guard'] = self.graph.new_ep('string')

  def get(self, vertice_or_edge, key):
    if type(vertice_or_edge) is gt.Vertex:
      return self.graph.vp[key][vertice_or_edge]
    elif type(vertice_or_edge) is gt.Edge:
      return self.graph.ep[key][vertice_or_edge]
    else:
      print(type(vertice_or_edge))
      return None

  def node(self,n):
    return self.graph.vp['name'][n]

  def parallel(self,n):
    return self.graph.vp['parallel'][n]

  def find_parallel(self,ary):
    for i,a in enumerate(self.graph.vp['parallel']):
      found = True
      for fa in ary:
        if fa not in a:
          found = False
      if found:
        return i
    return -1

  def parallel_difference(self,e):
    ss = set(self.parallel(e.source()))
    st = set(self.parallel(e.target()))
    return st.difference(ss)

  def edge(self,e):
    return self.graph.ep['trigger'][e]+'['+self.graph.ep['guard'][e]+']'

  def find_nodes(self,prop,match):
    return gt.find_vertex(self.graph,prop,match)

  def sample(self):
    return random.choice(self.graph.get_vertices())

  def edges_out(self,source,eprops=[]): # e.g. eprops = ['trigger','guard','distance']
    return self.graph.iter_out_edges(source, [self.graph.ep[prop] for prop in eprops])

  def view(self,filename,degree):
    u = gt.GraphView(self.graph, vfilt=lambda v: v.out_degree() > degree)
    tree = gt.min_spanning_tree(u)
    u = gt.GraphView(u, efilt=tree)
    gt.graph_draw(u, output=filename)

  def create_subgraph(self,from_node):
    g = Graken()
    for e in gt.bfs_iterator(self.graph, from_node):
      source = g.add_node(self.graph.vp['name'][e.source()])
      target = g.add_node(self.graph.vp['name'][e.target()])
      g.add_edge(source,target,self.graph.ep['distance'][e],self.graph.ep['trigger'][e],self.graph.ep['name'][e])
    return g

  def export_file(self,filename):
    self.graph.save(filename)

  def stats(self):
    if self.graph.num_vertices() == 0:
      print(self.graph.num_vertices(),'vertices',self.graph.num_edges(),'edges')
      return
    avgdeg, stddevdeg = gt.vertex_average(self.graph, 'total')
    avgwt, stddevwt = gt.edge_average(self.graph, self.graph.ep['distance'])

    print(str(self.graph.num_vertices()) + ' vertices and ' + str(self.graph.num_edges()) + ' edges')
    print('Average vertex degree',avgdeg,'standard deviation',stddevdeg)
    print('Average edge weight',avgwt,'standard deviation',stddevwt)

  def draw(self):
    res = gt.max_independent_vertex_set(self.graph)
    gt.graph_draw(
      self.graph,
      vertex_pen_width=2,
      edge_pen_width=4,
      vertex_fill_color=res,
      vertex_text=self.graph.vp['name'],
      vertex_font_size=10,
      vcmap=matplotlib.cm.plasma,
      output='../graph_named.png'
    )

  def search_parallel(self,source,states,subgoals=[]):
    def goal_checker(goals):
      def check_tar(tar,nodesf):
        found = True
        for g in goals:
          if g not in self.graph.vp['parallel'][tar]:
            found = False
            break
        return found
      return check_tar

    subgoals.append(states)
    visitors = []
    for sg in subgoals:
      if len(visitors) > 0:
        source = visitors[-1].found
      v = self.search_bfs(source,targetf=goal_checker(sg))
      if not v.found:
        return None
      visitors.append(v)
    path = []
    for v in visitors:
      path += v.get_path()
    return path

  def search(self,from_node,to_node):
    return gt.shortest_path(self.graph,from_node,to_node)

  def import_file(self,filename):
    logging.debug(str(self.__class__.__name__)+' -> '+str(stack()[0][3])+'() in '+str(__file__))
    logging.info('Import nodes')
    with closing(fi.input(filename)) as lines:
      i = 0
      for line in lines:
        line = line.strip()
        node_data = line.split(';')
        self.nodes[node_data[0]] = node = self.add_node(node_data[0])
        if node_data[1]:
          parallel = node_data[1].split(',')
          self.graph.vp['parallel'][node] = parallel
          for par in parallel:
            if par not in self.parallel_options:
              self.parallel_options.append(par)

    logging.info('Import edges')
    with closing(fi.input(filename)) as lines:
      for line in lines:
        line = line.strip()
        node_data = line.split(';')
        node = self.nodes[node_data[0]]
        if len(node_data) > 3:
          for edge in node_data[2:]:
            tar,dist,trig,guard = edge.split(',')
            distance = float(dist) if dist else 1.0
            self.add_edge(node,self.nodes[tar],distance,trig,guard)

  def add_node(self,name):
    node = self.graph.add_vertex()
    self.graph.vp['name'][node] = name
    return node

  def add_edge(self,from_node,to_node,distance=0.0,trigger='',guard='',name=''):
    edge = self.graph.add_edge(from_node,to_node)
    self.graph.ep['name'][edge] = name
    self.graph.ep['trigger'][edge] = trigger
    self.graph.ep['distance'][edge] = distance
    self.graph.ep['guard'][edge] = guard
    return edge

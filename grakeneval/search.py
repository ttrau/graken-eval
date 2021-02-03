import graph_tool.all as gt

class BFSVisitor(gt.BFSVisitor):
  def __init__(self, graph, target=None, targetf=None):
    self.graph = graph
    self.predecessor = graph.new_vertex_property('int64_t')
    for i in graph.vertices():
      self.predecessor[i] = -1
    self.distance = graph.new_vertex_property('int')
    self.edge = graph.new_vertex_property('int64_t')
    self.target = target
    self.found = None
    self.targetf = targetf

  def get_path(self,target=None):
    tar = target if target else self.found if self.found else self.target
    path = []
    while self.predecessor[tar] >= 0:
      edge = gt.find_edge(self.graph,self.graph.edge_index,self.edge[tar])[0]
      path.append(edge)
      tar = self.predecessor[tar]
    return list(reversed(path))

  def get_path_nodes(self,target=None):
    tar = target if target else self.found if self.found else self.target
    path = []
    while self.predecessor[tar] >= 0:
      path.append(self.predecessor[tar])
      tar = self.predecessor[tar]
    return list(reversed(path))

  def check_path(self,e):
    tar = e.target()
    sou = e.source()
    target_distance = self.distance[tar]
    current_distance = self.distance[sou] + 1

    if target_distance == 0 or target_distance > 0 and current_distance < target_distance:
      self.predecessor[tar] = sou
      self.distance[tar] = current_distance
      self.edge[tar] = self.graph.edge_index[e]

    if not self.found and self.target and self.target == tar:
      self.found = tar
      raise gt.StopSearch()
    elif not self.found and self.targetf and self.targetf(tar,self.get_path_nodes):
      self.found = tar
      raise gt.StopSearch()

  def tree_edge(self, e):
    self.check_path(e)

  #def gray_target(self,e):
  #  self.check_path(e)

  #def black_target(self,e):
  #  self.check_path(e)

def search_bfs(self,from_node,to_node=None,targetf=None):
  visitor = BFSVisitor(self.graph, target=to_node,targetf=targetf)
  gt.bfs_search(self.graph, from_node, visitor)
  return visitor

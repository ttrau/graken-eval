from subprocess import Popen, PIPE

class Graphviz:
  def __init__(self,title='graphviz',graph_type='digraph'):
    self.title = title
    self.layout = 'dot'
    self.graph_type = graph_type
    self.nodes = {}
    self.edges = []
    self.graph = {}
    self.node = {'shape':'box','fontname':'CMU Serif, Normal','penwidth':1.0,'fontsize':12}
    self.edge = {'fontname':'CMU Serif, Normal','penwidth':1.0,'len':0.2,'minlen':0.2,'arrowhead':'none'}
    self.params = ''

  def add_node(self,name,config={}):
    self.nodes[name] = config

  def add_edge(self,source,target,config={}):
    self.edges.append({'source':source,'target':target,'config':config})

  def viz(self,path=''):
    graph = self.graph_type+' '+self.title+' {'
    graph += '\n\t'+'\n\t'.join([str(k)+'=\"'+str(self.graph[k])+'\"' for k in self.graph])
    graph += '\n\tnode ['+','.join([str(k)+'=\"'+str(self.node[k])+'\"' for k in self.node])+']'
    graph += '\n\tedge ['+','.join([str(k)+'=\"'+str(self.edge[k])+'\"' for k in self.edge])+']'
    for n in self.nodes:
      graph += '\n\t'+str(n)+' ['+','.join([str(k)+'=\"'+str(self.nodes[n][k])+'\"' for k in self.nodes[n]])+'];'
    for e in self.edges:
      graph += '\n\t'+str(e['source'])+' -> '+str(e['target'])+' ['+','.join([str(k)+'=\"'+str(e['config'][k])+'\"' for k in e['config']])+'];'
    graph += '\n}\n'
    if path:
      f = open(path, "w")
      f.write(graph)
      f.close()
    return graph

  def to_svg(self,path=''):
    p = Popen(['/bin/'+self.layout, '-Tsvg'], stdout=PIPE, stdin=PIPE)
    p.stdin.write(str.encode(self.viz()))
    p.stdin.close()
    output = p.stdout.read().decode()
    if path:
      f = open(path, "w")
      f.write(output)
      f.close()
    return(output)

  def from_path(self,graken,edges=[],nodes=[]):
    self.layout = 'neato'
    self.params = ''
    self.node['label'] = ''
    self.node['height'] = '0.4'
    self.node['width'] = '0.4'
    self.edge['label'] = ''

    def add_block_at(i,id,label):
      pos = '0,'+str(i)+'!'
      pos_lab = str(1.6)+','+str(i)+'!'
      self.add_node(id,{'pos':pos,'shape':'rect','style':'filled','color':'black','height':'0.025','width':'0.2','label':'','fixedsize':'true'})
      self.add_node(id+'lab',{'pos':pos_lab,'label':label,'shape':'plaintext','labeljust':'l','width':'2.6','fixedsize':'true'})

    def add_trigger_at(i,step,id,trigger):
      pos = '0,'+str(i)+'!'
      self.add_node(id,{'pos':pos,'shape':'rect','label':str(step),'fixedsize':'true'})
      self.add_edge(id,id+'xtrig')
      pos_trigger = str(1.6)+','+str(i)+'!'
      self.add_node(id+'xtrig',{'pos':pos_trigger,'shape':'rect','label':trigger,'labeljust':'l','width':'2.6','fixedsize':'true'})

    elements = []
    for i,e in enumerate(edges):
      s = int(e.source())
      t = int(e.target())
      if i == 0:
        elements.append({'name':'n'+str(s),'node':s,'type':'state','label':graken.node(s)})

      name = 'n'+str(s)+'x'+str(t)
      trigger = graken.graph.ep['trigger'][e]
      if trigger:
        elements.append({'name':name,'node':s,'type':'trigger','trigger':trigger})

      diff = graken.parallel_difference(e)
      label = '\n'.join(diff) if len(diff) > 0 else graken.node(t)
      elements.append({'name':'n'+str(t),'node':s,'type':'state','label':label})

    cnt = 1
    for i,e in enumerate(elements):
      pos = (len(elements)-i)*0.4
      if i == 0:
        self.add_node(e['name'],{'pos':'0,'+str(pos+0.1)+'!','shape':'rect','label':'0','peripheries':'1','fixedsize':'true'})
        print('[0]')
      else:
        self.add_edge(elements[i-1]['name'],e['name'])
        print(' | ')
        if e['type'] == 'state':
          print('===--'+e['label'])
          add_block_at(pos,e['name'],e['label'])
        else:
          print('['+str(cnt)+']--['+e['trigger']+']')
          add_trigger_at(pos,cnt,e['name'],e['trigger'])
          cnt += 1

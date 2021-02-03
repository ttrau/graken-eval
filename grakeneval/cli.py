#!/usr/bin/env python
"""graken-eval"""

from sys import argv
from inspect import stack
import logging
import argparse
from cmd import Cmd
import re

from .grakeneval import Graken
from .viz import Graphviz

class GrakenCli(Cmd):
  def __init__(self, graken):
    Cmd.__init__(self)
    self.graken = graken
    self.source = graken.graph.vertex(0)
    self.target = graken.sample()
    self.history = []
    self.goal = []
    self.subgoals = []
    self.visitor = None

  def do_graph(self,text=''):
    self.graken.stats()

  def do_draw(self,text=''):
    self.graken.draw()

  def do_draw_subgraph(self,text=''):
    g = self.graken.create_subgraph(self.source)
    g.draw()

  def do_draw_visitor(self,text=''):
    if text and len(self.visitor) > 0:
      self.viz(text,edges=self.visitor)#.get_path())

  def do_random(self,text=''):
    self.history = []
    self.source = self.graken.sample()
    self.goal = self.graken.sample()

  def do_source(self,name=''):
    if not name:
      self.show_node(self.source)
    elif name in self.graken.nodes:
      self.history.append(self.source)
      self.source = self.graken.nodes[name]
    else:
      parallel = [par.strip() for par in name.split()]
      id = self.graken.find_parallel(parallel)
      if id > 0:
        self.source = id
      else:
        print("Not found:",name)

  def do_subgoal(self,name=''):
    if not name:
      print(self.subgoals)
    elif name == 'clear':
      self.subgoals = []
    else:
      cmds = [par.strip() for par in name.split()]
      if cmds[0] == 'add' and len(cmds) > 1:
        self.subgoals.append(cmds[1:])

  def do_goal(self,name=''):
    if not name:
      print(self.goal)
    else:
      self.goal = [par.strip() for par in name.split()]

  def do_target(self,name=''):
    if not name:
      self.show_node(self.target)
    elif name in self.graken.nodes:
      self.target = self.graken.nodes[name]
    else:
      parallel = [par.strip() for par in name.split()]
      id = self.graken.find_parallel(parallel)
      if id > 0:
        self.target = id
      else:
        print("Not found:",name)

  def do_history(self,name=''):
    if not name or name == 'short':
      print([self.graken.node(n) for n in self.history])
    elif name == 'long':
      for n in self.history:
        self.show_node(n)

  def do_find_parallel(self,name=''):
    if name:
      parallel = [par.strip() for par in name.split()]
      id = self.graken.find_parallel(parallel)
      if id > 0:
        self.show_node(id)

  def do_iter(self,text=''):
    cmds = [cmd.strip() for cmd in text.split()]
    edges_out = self.graken.edges_out(self.source,['trigger','guard','distance'])
    if len(cmds) > 0 and re.match("^[0-9]\d*$", cmds[0]):
      for i,edge in enumerate(edges_out):
        self.do_source(self.graken.node(edge[1])) if i == int(cmds[0]) else None
    elif len(cmds) > 0:
      self.do_source(cmds[0])
    else:
      for i,edge in enumerate(edges_out):
        ss = set(self.graken.parallel(edge[0]))
        st = set(self.graken.parallel(edge[1]))
        print('['+str(i)+']: --'+edge[2]+'['+edge[3]+']-->', self.graken.node(edge[1]), st.difference(ss))

  def do_import(self,path):
    self.graken.import_file(path)

  def do_search_path(self,text=''):
    vlist,elist = self.graken.search(self.source,self.target)
    print([self.graken.edge(e) for e in elist])
    if text:
      self.viz(text,elist,vlist)

  def do_follow_visitor(self,text=''):
    if self.visitor and len(self.visitor) > 0:
      self.source = self.visitor[-1].target()

  def do_search_parallel_path(self,name=''):
    if name:
      print('name:',name)
      self.do_goal(name)
    v = self.graken.search_parallel(self.source,self.goal,self.subgoals)
    self.visitor = v
    print('Distance:',len(v))

  def do_exit(self,name=''):
    exit(0)

  def show_node(self,id):
    print(self.graken.node(id))
    parallel = self.graken.parallel(id)
    if len(parallel) > 0:
      print(' '.join(parallel))

  def viz(self,path='',edges=[],nodes=[]):
    v = Graphviz()
    v.from_path(self.graken,edges,nodes)

    if path and path.endswith('.dot'):
      v.viz(path)
    elif path:
      v.to_svg(path)

  def completedefault(self,text,line,si,ei):
    cmds = [cmd.strip() for cmd in line.split()]
    cmds.append('') if len(cmds) == 1 else None
    if cmds[0] in ['source','target']:
      return self.match_from(self.graken.nodes.keys(),cmds[-1])
    elif cmds[0] in ['find_parallel','search_parallel_path']:
      return self.match_from(self.graken.parallel_options,cmds[-1])
    elif cmds[0] == 'iter':
      edges_out = self.graken.edges_out(self.source)
      return self.match_from([self.graken.node(e[1]) for e in edges_out],cmds[-1])
    elif cmds[0] == 'history':
      if len(cmds) > 1:
        return self.match_from(['short','long'],cmds[-1])
    elif cmds[0] == 'subgoal':
      if len(cmds) == 1:
        return self.match_from(['add','clear'],cmds[-1])
      elif len(cmds) > 1:
        return self.match_from(self.graken.parallel_options,cmds[-1])
    return []

  def match_from(self,list,match):
    n = len(match.strip())
    matches = []
    for key in list:
      if n > 0 and key[:n] == match:
        matches.append(key)
      elif n == 0:
        matches.append(key)

    if len(matches) > 50:
      return matches[0:50]
    return matches

def get_args():
  parser = argparse.ArgumentParser(description='Process a graph.')
  parser.add_argument('PATH', help='<Required> PATH to graph file.')
  parser.add_argument('-o', '--out', help='PATH [string] to OUT.')
  parser.add_argument('--graphml', help='Graphml file to OUT.', action='store_true')
  parser.add_argument('--view', help='View with vertex filter DEGREE [int] to OUT.',type=int)
  parser.add_argument('--dpath', help='Flag to draw the path found in the visitor object.', action='store_true')
  parser.add_argument('--source', help='SOURCE [string] node for search algorithm.')
  parser.add_argument('--psource', help='Add parallel stats in source: --psource ps1 ps2 ps2 ...', nargs='+')
  parser.add_argument('--target', help='TARGET [string] node for search algorithm.')
  parser.add_argument('--ptarget', help='Add parallel stats in target: --ptarget ps1 ps2 ps2 ...', nargs='+')
  parser.add_argument('--pfind', help='Find path to parallel target: --pfind ps1 ps2 ps2 ...', nargs='+')
  parser.add_argument('-I', '--interactive', help='Flag to open interactive shell.', action='store_true')
  parser.add_argument('-i', '--info', help='Info logging.', action="store_const", dest="log", const=logging.INFO)
  parser.add_argument('-d', '--debug', help='Debug logging.', action="store_const", dest="log", const=logging.DEBUG)
  return parser.parse_args()

def main():
  args = get_args()
  logging.basicConfig(level=args.log)
  logging.debug(str(stack()[0][3])+'() in '+str(__file__))
  logging.info('Arguments:'+str(args))

  g = Graken()
  if args.PATH:
    print(args.PATH)
    g.import_file(args.PATH)
  if args.out:
    if args.graphml:
      logging.info('Export graphml to '+args.out+'.graphml')
      g.export_file(args.out+'.graphml')
    if args.view:
      logging.info('Export view with degree '+args.view+' to '+args.out+'.png')
      g.view(args.out+'.png',int(args.view))

  logging.info('Starting Cli Tool...')
  cli = GrakenCli(g)
  if args.target:
    logging.info('Setting target to ' + args.target)
    cli.do_target(args.target)
  if args.source:
    logging.info('Setting source to ' + args.source)
    cli.do_source(args.source)
  if args.psource:
    id = cli.graken.find_parallel(args.psource)
    if id > 0:
      cli.do_source(cli.graken.node(id))
  if args.ptarget:
    id = cli.graken.find_parallel(args.ptarget)
    if id > 0:
      cli.do_target(cli.graken.node(id))
  if args.pfind:
    cli.visitor = cli.graken.search_parallel(cli.source,args.pfind)
  if args.pfind:
    cli.visitor = cli.graken.search_parallel(cli.source,args.pfind)
  if args.out and args.dpath:
    logging.info('Exporting found path to '+args.out+'.svg')
    cli.viz(args.out+'.svg',edges=cli.visitor.get_path())


  if args.interactive:
    cli.cmdloop()

  exit(0)

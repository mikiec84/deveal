from __future__ import unicode_literals

__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>"


##############################################################################
##############################################################################

import os
import jinja2
import argparse
import shutil
import yaml
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


##############################################################################
##############################################################################


BaseDir = os.path.dirname(os.path.abspath(__file__))
SkeletonDir = os.path.join(BaseDir,"skeleton")

DefaultConfig = {
  "reveal_theme" : "black",
  "reveal_path" : "https://cdn.jsdelivr.net/npm/reveal.js@3.6.0"
}


##############################################################################
##############################################################################


class Deveal(FileSystemEventHandler):

  def __init__(self):
    pass


##############################################################################


  def __printError(self,Msg):
    print("[ERROR] %s" % Msg)


##############################################################################


  def __printWarning(self,Msg):
    print("[WARNING] %s" % Msg)


##############################################################################


  def __buildVars(self):
    Vars = dict()

    if not os.path.isfile("deveal.yaml"):
      self.__printWarning("File deveal.yaml not found")
    else:
      with open(os.path.join(os.getcwd(),"deveal.yaml"), 'r') as YAMLFile:
        try:
          Vars = yaml.load(YAMLFile)
        except yaml.YAMLError as E:
          Mark = E.problem_mark
          self.__printWarning("Problem reading deveal.yaml file at line %s, column %s. Config file ignored." % (Mark.line+1,Mark.column+1))

    for (Key, Value) in DefaultConfig.items():
      if Key not in Vars:
        Vars[Key] = Value
        self.__printWarning("Missing parameter %s in configuration, using defaullt value \"%s\"" % (Key,Value))

    return Vars


##############################################################################


  def runNew(self,Args):
    DestDir = os.path.join(os.getcwd(),Args['path'])
    print("Creating new slideshow in %s..." % DestDir)
    shutil.copytree(SkeletonDir,DestDir)
    print("Done")

    return 0


##############################################################################


  def runBuild(self,Args):
    Vars = self.__buildVars()

    try:
      TplFilename = "deveal-index.html"
      GeneratedContent = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd())).get_template(TplFilename).render(**Vars)
    except jinja2.TemplateError as E:
      self.__printError("Template problem : %s (file %s, line %s)" % (E.message,E.filename,E.lineno))
      return 127

    OutFile = open(os.path.join(os.getcwd(),"index.html"),"w")
    OutFile.write(GeneratedContent)
    OutFile.close()

    print("Build on %s" % time.strftime("%Y-%d-%m %H:%M:%S"))

    return 0


##############################################################################


  def on_any_event(self, event):
    if event.src_path != os.path.join(os.getcwd(),"index.html"):
      print("%s is %s" % (os.path.relpath(event.src_path),event.event_type))
      self.runBuild(dict())


##############################################################################


  def runWatch(self,Args):
    print("Watching %s ..." % os.getcwd())
    Obs = Observer(timeout=0.1)
    Obs.schedule(self, path=os.getcwd(), recursive=True)
    Obs.start()

    try:
      while True:
        time.sleep(1)
    except KeyboardInterrupt:
      print("")
      print("Interrupted by keyboard...")
      Obs.stop()

    Obs.join()
    print("Done")

    return 0


##############################################################################
##############################################################################


def main():

  Parser = argparse.ArgumentParser(description="Helper tool for creation and management of reveal.js slideshows")

  SubParsers = Parser.add_subparsers(dest="command_name")

  ParserNew = SubParsers.add_parser("new",help="create new reveal.js slideshow")
  ParserNew.add_argument("path",type=str)
  ParserBuild = SubParsers.add_parser("build",help="build reveal.js slideshow")
  ParserWatch = SubParsers.add_parser("watch",help="watch for changes and build reveal.js slideshow")

  Args = vars(Parser.parse_args())

  Dvl = Deveal()

  if Args["command_name"] == "new":
    return Dvl.runNew(Args)
  elif Args["command_name"] == "build":
    return Dvl.runBuild(Args)
  elif Args["command_name"] == "watch":
    return Dvl.runWatch(Args)

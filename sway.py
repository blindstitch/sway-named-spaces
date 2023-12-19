import dmenu
from box import Box

from shlex import split
from subprocess import Popen, run, PIPE
from json import loads
from pprint import PrettyPrinter as pppp; ppp=pppp()
import re
from random import choice
import os
cwd = os.path.dirname(os.path.realpath(__file__))


# Helpers
def base(s): return re.sub(r"\d+:","",s)
sm = lambda s: run(split("swaymsg "+s))

# New workspace randome names
namesfile = cwd+'vegetables.txt'
def randname(): return choice(open(namesfile,'r').read().strip().split('\n'))


class SwaySpaces(object):
    def __init__(self):
        self.refresh()

    # The script is mostly stateless so some things might not work when running it
    # in a python kernel, but it seems to be stable when invoking through sway

    # Reindex is here to keep it faster when the changes are occurring in
    # place, like move() which is supposed to fix up the names as it goes along

    def refresh(self,reindex=False):
        sp = Popen(split("swaymsg -t get_workspaces --raw"),stdout=PIPE,stderr=PIPE)
        stdout,stderr = sp.communicate()
        self.dicts = loads(stdout)

        for i,d in enumerate(self.dicts):
            self.dicts[i] = Box(self.dicts[i])
        for ws in self.dicts:
            ws['basename'] = base(ws['name'])

        self.outputs = list(set([ws.output for ws in self.dicts]))

        for output in self.outputs:
            for i,ws in enumerate(self.spaces(output)):
                ws['output_idx'] = i
                ws['output_idx_sway'] = i+1

            # Helper bools for moving
            self.spaces(output)[0]['first'] = True
            self.spaces(output)[-1]['last'] = True
            for ws in self.spaces(output)[1:]:
                ws['first'] = False
            for ws in self.spaces(output)[:-1]:
                ws['last'] = False
                
        # Rename everything
        # Supposed to set it manually in the args
        if reindex:
            for output in self.outputs:
                for i,ws in enumerate(self.spaces(output)):
                    fixed_name = f"{ws.output_idx_sway}:{ws.basename}"
                    sm(f"rename workspace {ws.name} to {fixed_name}")
                    ws.name = fixed_name


        # For output cycling, which is not really implemented yet
        self.output_idx = self.outputs.index(self.focused(refresh=False).output)


    def new(self):
        # The new name cannot be in the current names so try to fix that.
        sm("workspace 10000:"+randname())
        self.refresh(reindex=True)

    def focused(self,offset=0,refresh=False): # Offset is poorly named, it gives the workspace to left (negative) or right(positive)
        if refresh: # hack to let it be used in refresh() without recursion
            self.refresh()

        focusedspace = list(filter(lambda ws: ws['focused'], self.dicts))[0]
         
        match offset:
            case 0:
               return focusedspace
            case 'left': offset=-1
            case 'right': offset=1

        numspaces = len(self.spaces('current'))
        gotoidx = focusedspace.output_idx+offset
        return self.spaces('current')[gotoidx % numspaces]

    def output(self,step=0):
        self.refresh()

        match step:
            case 0: return self.focused().output
            case 'cycle_forward': step=1
            case 'cycle_back': step=-1

        curr_idx = self.outputs.index(self.focused().output)
        return self.outputs[(curr_idx+step) % len(self.outputs)]

    def find(self,search):
        result = list(filter(lambda ws: ws.basename == search, self.dicts))[0]
        if len(result) != 0:
            return result
        else:
            return None

    def spaces(self,output=None,key=None):
        match output:
            case None:
                if key: return [ws[key] for ws in self.dicts]
                else: return self.dicts
            case 'current':
                currspace = list(filter(lambda ws: ws.output == self.focused().output, self.dicts))
                if key: return [ws[key] for ws in currspace]
                else: return currspace
            case other:
                currspace = list(filter(lambda ws: ws.output == output, self.dicts))
                if len(currspace) == 0:
                    raise Exception('Space does not exist')
                else:
                    if key: return [ws[key] for ws in currspace]
                    else: return currspace


    def names(self,output=None,base=False):
        if not base:
            return self.spaces(output,key='name')
        else: 
            return self.spaces(output,key='basename')


    def rename(self,newname): # Expects a dmenu.show(['']) when called
        if newname == '':
            print("No new name given, doing nothing")
        elif newname == self.focused().basename:
            print("New workspace name matches the old one")
        else:
            if newname in self.names(base=True):
                print("That name is already in the current list")
            else:
                sm(f"rename workspace {self.focused().name} to {self.focused().output_idx+1}:{newname}")

        self.refresh(reindex=True)


    def go(self,dest):
        result = self.find(dest)
        if result:
            sm("workspace "+result.name)
        else:
            print('workspace not found')

    def move_workspace(self,direction):
        spaces = self.spaces('current')
        i = self.focused().output_idx

        def make_newnames(spaceslist,sparse=True):
            oldnames = [s.name for s in spaces]
            newnames = [f"{i+1}:{s.basename}" for i,s in enumerate(spaces)]
            zipped = list(zip(oldnames,newnames))
            if sparse: zipped = list(filter(lambda t2: t2[0] != t2[1], zipped))
            return zipped

        match direction:
            case 'left':
                if self.focused().first:
                    print("Can't go any further left")
                else:
                    # Semicolons allow for multiple commands, might not be necessary
                    sm(f"rename workspace {self.focused().name} to {i+1}:{self.focused().basename}; "+
                    f"rename workspace {self.focused(-1).name} to {i+2}:{self.focused(-1).basename}")

                    # These wouldn't be necessary if i could get the dang names right!
                    self.refresh(reindex=True)

            case 'right':
                if self.focused().last:
                    print("Can't go any further right")
                else:
                    # Done as separate commands
                    # This one
                    sm(f"rename workspace {self.focused().name} to {i+2}:{self.focused().basename}")
                    # Other
                    sm(f"rename workspace {self.focused(1).name} to {i+1}:{self.focused(1).basename}")

                    self.refresh(reindex=True)

            case 'next_output':
                if len(self.outputs) == 1:
                    print("there's no other monitor to go to")
                else:
                    sm(f"move workspace to output {self.output(1)}")
                    sm(f"rename workspace {self.focused().name} to 9999:{self.focused().basename}")
                    self.refresh(reindex=True)

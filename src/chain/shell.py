import direct.directbase.DirectStart
from direct.gui.DirectGui import DirectEntry
from direct.gui.OnscreenText import OnscreenText 
from pandac.PandaModules import TextNode

# top line is a hack, to preserve the width
# generated with: figlet -f slant "Chain of Command"
WELCOME = """-------------------------------------------------------------------------------
\n\n\n\n\n\n\n\n\n\n
   ________          _                ____
  / ____/ /_  ____ _(_)___     ____  / __/
 / /   / __ \/ __ `/ / __ \   / __ \/ /_  
/ /___/ / / / /_/ / / / / /  / /_/ / __/  
\____/_/ /_/\__,_/_/_/ /_/   \____/_/     
                                          
   ______                                          __
  / ____/___  ____ ___  ____ ___  ____ _____  ____/ /
 / /   / __ \/ __ `__ \/ __ `__ \/ __ `/ __ \/ __  / 
/ /___/ /_/ / / / / / / / / / / / /_/ / / / / /_/ /  
\____/\____/_/ /_/ /_/_/ /_/ /_/\__,_/_/ /_/\__,_/   

"""

class Shell:
    def __init__(self):
        font = loader.loadFont('../../models/FreeMono.ttf')
        self.output = OnscreenText(text=WELCOME, pos=(-1,1), scale=0.07,align=TextNode.ALeft,mayChange=True, bg=(0,0,0,1), fg=(1,1,1,0.8), font=font)
        self.prompt = "> "
        self.input = DirectEntry(scale=0.07, command=self.parse_cmd, focus=1)
        self.input.enterText(self.prompt)
    
    def append_line(self,txt):
        lines = self.output.getText().split('\n')
        del lines[1] # preserve topline, scroll
        lines.append(txt)
        self.output.setText('\n'.join(lines))
    
    def parse_cmd(self,str):
        cmd = str.lstrip(self.prompt).split()
        #TODO: actually do something with the cmd
        self.append_line("got cmd: %s" % '_'.join(cmd))
        self.input.enterText(self.prompt)
        self.input.setFocus()

if __name__ == "__main__":
    Shell()
    run()

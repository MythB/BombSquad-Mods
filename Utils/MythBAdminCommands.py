import bs                           #Created By MythB # http://github.com/MythB
import bsInternal
import bsPowerup
import bsUtils
import random
import os
import MythBAdminList as mbal

class chatOptions(object):
    def __init__(self):
        self.MythBWasHere = True
    def checkDevice(self,nick):# check if in adminlist
        client_str = []
        for i in bsInternal._getForegroundHostSession().players:#FIXME "unicode characters lenght" !!!
            if i.getName().encode('utf-8') == nick: # use i.getName(True) <-- if u need fullname
               client_str = i.get_account_id()
        if client_str in mbal.AdminList:
            return True
        else:
            #bsInternal._chatMessage("Commands Only For Admins")
            return False
        #bs.gameTimer(100,call=self.checkDevice,repeat=True)
        
    def opt(self,nick,msg):
        if self.checkDevice(nick):
            m = msg.split(' ')[0] # command
            a = msg.split(' ', 1)[1:] # arguments
            
            activity = bsInternal._getForegroundHostActivity()
            with bs.Context(activity):
                if m == '/kick': #just remove from the game
                    if a == []:
                        bsInternal._chatMessage("MUST USE KICK ID")
                    else:
                        try:
                            kickedPlayerID = int(a[0])
                        except Exception: 
                            bsInternal._chatMessage("PLAYER NOT FOUND")
                        else:
                            if not kickedPlayerID == -1:
                               bsInternal._disconnectClient(kickedPlayerID)
                            else:
                               bsInternal._chatMessage("CANT KICK HOST")

                elif m == '/list': #list of current players id
                    bsInternal._chatMessage("==========PLAYER KICK IDS==========")
                    for i in bsInternal._getGameRoster():
                        try:
                            bsInternal._chatMessage(i['players'][0]['nameFull'] + "     kick ID " + str(i['clientID']))
                        except Exception:
                            pass
                    bsInternal._chatMessage("==========PLAYER IDS=============")
                    for s in bsInternal._getForegroundHostSession().players:
                        bsInternal._chatMessage(s.getName() +"  ID = "+ str(bsInternal._getForegroundHostSession().players.index(s)))
                       
                elif m == '/ban':# add id to banlist=autokick list
                    if a == []:
                       bsInternal._chatMessage("MUST USE PLAYER ID OR NICK")
                    else:               #try nick if nick's lenght is more then 2 else try player id FIX ME !!!
                      if len(a[0]) > 2:
                        for i in bs.getActivity().players:
                            try:
                                if (i.getName()).encode('utf-8') == (a[0]):
                                   bannedClient = i.getInputDevice().getClientID()
                                   bannedName = i.getName().encode('utf-8')
                                   bannedPlayerID = i.get_account_id()
                                   foolist = []
                                   foolist = mbal.autoKickList
                                   if bannedPlayerID not in foolist:
                                      foolist.append(bannedPlayerID)
                                      bsInternal._chatMessage(str(bannedName) + " Banned")
                                      i.removeFromGame()
                                   else:
                                      bsInternal._chatMessage(str(bannedName) + " Already Banned")
                                   with open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py") as file:
                                        s = [row for row in file]
                                        s[7] = 'autoKickList = '+ str(foolist) + '\n'
                                        f = open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py",'w')
                                        for i in s:
                                            f.write(i)
                                        f.close()
                                        reload(mbal)
                            except Exception:
                                pass
                      else:
                          try: 
                              bannedClient = bsInternal._getForegroundHostSession().players[int(a[0])]
                          except Exception: 
                              bsInternal._chatMessage("PLAYER NOT FOUND")
                          else:
                              foolist = []
                              foolist = mbal.autoKickList
                              bannedPlayerID = bannedClient.get_account_id()
                              if bannedPlayerID not in foolist:
                                 foolist.append(bannedPlayerID)
                                 bsInternal._chatMessage(str(bannedClient) + " Banned")
                                 bannedClient.removeFromGame()
                              else:
                                 bsInternal._chatMessage(str(bannedClient) + " Already Banned")
                              with open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py") as file:
                                   s = [row for row in file]
                                   s[7] = 'autoKickList = '+ str(foolist) + '\n'
                                   f = open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py",'w')
                                   for i in s:
                                       f.write(i)
                                   f.close()
                                   reload(mbal)

                elif m == '/unban':# remove id from banlist=autokick list
                    if a == []:
                       bsInternal._chatMessage("MUST USE PLAYER ID OR NICK")
                    else:
                      if len(a[0]) > 2:
                        for i in bs.getActivity().players:
                            try:
                                if (i.getName()).encode('utf-8') == (a[0]):
                                   bannedClient = i.getInputDevice().getClientID()
                                   bannedName = i.getName().encode('utf-8')
                                   bannedPlayerID = i.get_account_id()
                                   foolist = []
                                   foolist = mbal.autoKickList
                                   if bannedPlayerID in foolist:
                                      foolist.remove(bannedPlayerID)
                                      bsInternal._chatMessage(str(bannedName) + " be free now!")
                                   else:
                                      bsInternal._chatMessage(str(bannedName) + " Already Not Banned")
                                   with open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py") as file:
                                        s = [row for row in file]
                                        s[7] = 'autoKickList = '+ str(foolist) + '\n'
                                        f = open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py",'w')
                                        for i in s:
                                            f.write(i)
                                        f.close()
                                        reload(mbal)
                            except Exception:
                                pass
                      else:
                          try: 
                              bannedClient = bsInternal._getForegroundHostSession().players[int(a[0])]
                          except Exception: 
                              bsInternal._chatMessage("PLAYER NOT FOUND")
                          else:
                              foolist = []
                              foolist = mbal.autoKickList
                              bannedPlayerID = bannedClient.get_account_id()
                              if bannedPlayerID in foolist:
                                 foolist.remove(bannedPlayerID)
                                 bsInternal._chatMessage(str(bannedClient) + " be free now!")
                              else:
                                 bsInternal._chatMessage(str(bannedClient) + " Already Not Banned")
                              with open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py") as file:
                                   s = [row for row in file]
                                   s[7] = 'autoKickList = '+ str(foolist) + '\n'
                                   f = open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py",'w')
                                   for i in s:
                                       f.write(i)
                                   f.close()
                                   reload(mbal)
                        
                elif m == '/amnesty': # reset blacklist
                    foolist = []
                    bsInternal._chatMessage("==========FREEDOM TO ALL==========")
                    bsInternal._chatMessage("=========BLACKLİST WIPED=========")
                    with open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py") as file:
                        s = [row for row in file]
                        s[7] = 'autoKickList = '+ str(foolist) + '\n'
                        f = open(bs.getEnvironment()['systemScriptsDirectory'] + "/MythBAdminList.py",'w')
                        for i in s:
                            f.write(i)
                        f.close()
                        reload(mbal)

                elif m == '/camera': #change camera mode
                    try:
                        if bs.getSharedObject('globals').cameraMode == 'follow':
                            bs.getSharedObject('globals').cameraMode = 'rotate'
                        else:
                            bs.getSharedObject('globals').cameraMode = 'follow'
                    except Exception:
                        bsInternal._chatMessage('AN ERROR OCCURED')
                        
                elif m == '/maxplayers': #set maxplayers limit
                    if a == []:
                        bsInternal._chatMessage('MUST USE NUMBERS')
                    else:
                        try:
                            bsInternal._getForegroundHostSession()._maxPlayers = int(a[0])
                            bsInternal._setPublicPartyMaxSize(int(a[0]))
                            bsInternal._chatMessage('MaxPlayers = '+str(int(a[0])))
                        except Exception:
                            bsInternal._chatMessage('AN ERROR OCCURED')

                elif m == '/help': #show help
                        bsInternal._chatMessage("=====================COMMANDS=====================")
                        bsInternal._chatMessage("list-kick-remove-ban-unban-amnesty-kill-curse-end-heal")
                        bsInternal._chatMessage("freeze-thaw-headless-shield-punch-maxplayers-headlessall")
                        bsInternal._chatMessage("killall-freezeall-shieldall-punchall-camera-slow-gj")
                        
                elif m == '/remove': #remove from game
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      i.removeFromGame()
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].removeFromGame()
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/curse': #curse
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.curse()
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.curse()
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/curseall': #curse all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.curse()
                            except Exception:
                                pass
                     
                elif m == '/kill': #kill
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.node.handleMessage(bs.DieMessage())
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.node.handleMessage(bs.DieMessage())
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/killall': #kill all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.node.handleMessage(bs.DieMessage())
                            except Exception:
                                pass
                     
                elif m == '/freeze': #freeze
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.node.handleMessage(bs.FreezeMessage())
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.node.handleMessage(bs.FreezeMessage())
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/freezeall': #freeze all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.node.handleMessage(bs.FreezeMessage())
                            except Exception:
                                pass
                     
                elif m == '/thaw': #thaw
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.node.handleMessage(bs.ThawMessage())
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.node.handleMessage(bs.ThawMessage())
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/thawall': #thaw all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.node.handleMessage(bs.ThawMessage())
                            except Exception:
                                pass
                     
                elif m == '/headless': #headless
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.node.headModel = None
                                         i.actor.node.style = "cyborg"
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.node.headModel = None
                                 bs.getActivity().players[int(a[0])].actor.node.style = "cyborg"
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/headlessall': #headless all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.node.headModel = None
                                   i.actor.node.style = "cyborg"
                            except Exception:
                                pass
                     
                elif m == '/heal': #heal
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.node.handleMessage(bs.PowerupMessage(powerupType = 'health'))
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.node.handleMessage(bs.PowerupMessage(powerupType = 'health'))
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/healall': #heal all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.node.handleMessage(bs.PowerupMessage(powerupType = 'health'))
                            except Exception:
                                pass
                     
                elif m == '/shield': #shield
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.node.handleMessage(bs.PowerupMessage(powerupType = 'shield'))
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.node.handleMessage(bs.PowerupMessage(powerupType = 'shield'))
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/shieldall': #shield all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.node.handleMessage(bs.PowerupMessage(powerupType = 'shield'))
                            except Exception:
                                pass

                elif m == '/punch': #punch
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.node.handleMessage(bs.PowerupMessage(powerupType = 'punch'))
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.node.handleMessage(bs.PowerupMessage(powerupType = 'punch'))
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/punchall': #punch all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.node.handleMessage(bs.PowerupMessage(powerupType = 'punch'))
                            except Exception:
                                pass

                elif m == '/knock': #knock him
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.node.handleMessage("knockout",5000)
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.node.handleMessage("knockout",5000)
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/knockall': #knock all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.node.handleMessage("knockout",5000)
                            except Exception:
                                pass
                     
                elif m == '/celebrate': #celebrate him
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      if i.actor.exists():
                                         i.actor.node.handleMessage('celebrate', 30000)
                               except Exception:
                                   pass
                        else:
                             try:
                                 bs.getActivity().players[int(a[0])].actor.node.handleMessage('celebrate', 30000)
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')
                                 
                elif m == '/celebrateall': #celebrate all
                     for i in bs.getActivity().players:
                            try:
                                if i.actor.exists():
                                   i.actor.node.handleMessage('celebrate', 30000)
                            except Exception:
                                pass

                elif m == '/slow': # slow-mo
                    try:
                        if bs.getSharedObject('globals').slowMotion == True:
                           bs.getSharedObject('globals').slowMotion = False
                        else:
                            bs.getSharedObject('globals').slowMotion = True
                    except Exception:
                        bsInternal._chatMessage('AN ERROR OCCURED')

                elif m == '/end': # just finish the game
                    try:
                        bsInternal._getForegroundHostActivity().endGame()
                        bsInternal._chatMessage('THE END')
                    except Exception:
                        bsInternal._chatMessage('AN ERROR OCCURED')
                        
                elif m == '/gj': #good job! 
                    if a == []:
                        bsInternal._chatMessage('MUST USE PLAYER ID OR NICK')
                    else:
                        if len(a[0]) > 2:
                           for i in bs.getActivity().players:
                               try:
                                   if (i.getName()).encode('utf-8') == (a[0]):
                                      activity.showZoomMessage(' Good Job!  '+i.getName())
                               except Exception:
                                   pass
                        else:
                             try:
                                 activity.showZoomMessage(' Good Job! ')
                             except Exception:
                                 bsInternal._chatMessage('PLAYER NOT FOUND')

c = chatOptions()

def cmd(msg):
    if bsInternal._getForegroundHostActivity() is not None:
        n = msg.split(': ')
        c.opt(n[0],n[1])
bs.realTimer(5000,bs.Call(bsInternal._setPartyIconAlwaysVisible,True))
import bsUI
bs.realTimer(10000,bs.Call(bsUI.onPartyIconActivate,(0,0)))## THATS THE TRICKY PART check ==> 23858 bsUI / _handleLocalChatMessage "MemoryLeak FIXED"

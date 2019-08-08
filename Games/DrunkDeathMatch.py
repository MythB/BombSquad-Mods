import bs      #just a test its not working well #Created By MythB # http://github.com/MythB
import bsMap
import random
import math
import bsVector
import bsUtils


def bsGetAPIVersion():
    # see bombsquadgame.com/apichanges
    return 4

def bsGetGames():
    return [DrunkDeathMatchGame]
    
    
    
class NightMod(bs.Actor):

    def __init__(self,position=(0,1.5,0)):
        bs.Actor.__init__(self)

        activity = self.getActivity()
        
        # spawn just above the provided point
        self._spawnPos = (position[0],position[1]+0.3,position[2])
        self.node = bs.newNode("prop",
                               attrs={'model': activity._nightModel,
                                      'colorTexture': activity._nightTex,
                                      'body':'sphere',
                                      'reflection':'soft',
                                      'bodyScale': 0.1,
                                      'modelScale':0.001,
                                      'density':0.010,
                                      'reflectionScale':[0.23],
                                      'shadowSize': 999999.0,
                                      'isAreaOfInterest':True,
                                      'position':self._spawnPos,
                                      'materials': [bs.getSharedObject('objectMaterial'),activity._nightMaterial]
                                      },
                               delegate=self)

    def handleMessage(self,m):
             bs.Actor.handleMessage(self,m)

class DrunkDeathMatchGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Drunk Death Match'

    @classmethod
    def getDescription(cls,sessionType):
        return 'Kill a set number of enemies to win.'

    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if (issubclass(sessionType,bs.TeamsSession)
                        or issubclass(sessionType,bs.FreeForAllSession)) else False

    @classmethod
    def getSupportedMaps(cls,sessionType):
        return ['Rampage','Football Stadium']
        
        
    @classmethod
    def getSettings(cls,sessionType):
        settings = [("Kills to Win Per Player",{'minValue':1,'default':5,'increment':1}),
                    ("Time Limit",{'choices':[('None',0),('1 Minute',60),
                                              ('2 Minutes',120),('5 Minutes',300),
                                              ('10 Minutes',600),('20 Minutes',1200)],'default':0}),
                    ("Respawn Times",{'choices':[('Shorter',0.25),('Short',0.5),('Normal',1.0),('Long',2.0),('Longer',4.0)],'default':1.0}),
                    ("Night Mode",{'default':False})]
        
        # In teams mode, a suicide gives a point to the other team, but in free-for-all it
        # subtracts from your own score. By default we clamp this at zero to benefit new players,
        # but pro players might like to be able to go negative. (to avoid a strategy of just
        # suiciding until you get a good drop)
        if issubclass(sessionType, bs.FreeForAllSession):
            settings.append(("Allow Negative Scores",{'default':False}))

        return settings

    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)
        
        self._nightModel = bs.getModel("shield")
        self._nightTex = bs.getTexture("black")

        # print messages when players die since it matters here..
        self.announcePlayerDeaths = True
        
        self._scoreBoard = bs.ScoreBoard()

        self._nightMaterial = bs.Material()
        self._nightMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('pickupMaterial')),'or',
                        ('theyHaveMaterial',bs.getSharedObject('attackMaterial'))),
            actions=(('modifyPartCollision','collide',False)))

        # we also dont want anything moving it
        self._nightMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('objectMaterial')),'or',
                        ('theyDontHaveMaterial',bs.getSharedObject('footingMaterial'))),
            actions=(('modifyPartCollision','collide',False),
                     ('modifyPartCollision','physical',False)))
                     #drunk
        self._scoreRegionMaterial = bs.Material()
        self._scoreRegionMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('objectMaterial')),'or',
                        ('theyDontHaveMaterial',bs.getSharedObject('footingMaterial'))),
            actions=(('modifyPartCollision','collide',True),
                     ('modifyPartCollision','physical',True)))
                     
        self._scoreRegionMaterial.addActions(conditions=("theyHaveMaterial",bs.getSharedObject('playerMaterial')),
                                      actions=(("call","atConnect",self._DrunkPlayerCollide),))


    def getInstanceDescription(self):
        return ('Crush ${ARG1} of your enemies.',self._scoreToWin)

    def getInstanceScoreBoardDescription(self):
        return ('kill ${ARG1} enemies',self._scoreToWin)

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Night Mode'] else 'ToTheDeath')

    def onTeamJoin(self,team):
        team.gameData['score'] = 0
        if self.hasBegun(): self._updateScoreBoard()

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)

        self.setupStandardTimeLimit(self.settings['Time Limit'])
        self.setupStandardPowerupDrops()
        if len(self.teams) > 0:
            self._scoreToWin = self.settings['Kills to Win Per Player'] * max(1,max(len(t.players) for t in self.teams))
        else: self._scoreToWin = self.settings['Kills to Win Per Player']
        self._updateScoreBoard()
        self._dingSound = bs.getSound('dingSmall')
        if self.settings['Night Mode']: self._nightSpawny()
        #self.cameraFlash(duration=10)

        
        _scaleFoot = (29.0,0.02,11.8)
        _scaleRamp = (14.0,0.1,4.33)
        _posFoot = (0.0,0.0,0.0)
        _posRamp = (0.3196701116, 5.0, -4.292515158)
        _typeFoot =('box')
        _typeRamp =('box')
        
        
        Mapinfo = self.getMap()
        if Mapinfo.getName() ==('Football Stadium'): self._mapScale = _scaleFoot
        if Mapinfo.getName() ==('Football Stadium'): self._mapPos = _posFoot
        if Mapinfo.getName() ==('Football Stadium'): self._mapType = _typeFoot
        if Mapinfo.getName() ==('Rampage'): self._mapScale = _scaleRamp
        if Mapinfo.getName() ==('Rampage'): self._mapPos = _posRamp
        if Mapinfo.getName() ==('Rampage'): self._mapType = _typeRamp
        
        self._scoreRegions = []
        self._scoreRegions.append(bs.NodeActor(bs.newNode("region",
                                                          attrs={'position': self._mapPos,
                                                                 'type':self._mapType,
                                                                'scale': self._mapScale,
                                                                 'materials':[self._scoreRegionMaterial]})))
                                                                 
        # ****** The Pad config *****
        #if Mapinfo.getName() ==('The Pad'): self._mapScale = _scalePad
        #if Mapinfo.getName() ==('The Pad'): self._mapPos = _posPad
        #if Mapinfo.getName() ==('The Pad'): self._mapType = _typePad
        #_posPad = (0.0, 3.195, -3.0)
        #_scalePad = (12.0,0.1,12.0)
        #_typePad =('box')

    def handleMessage(self,m):

        if isinstance(m,bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self,m) # augment standard behavior

            player = m.spaz.getPlayer()
            self.respawnPlayer(player)

            killer = m.killerPlayer
            if killer is None: return

            # handle team-kills
            if killer.getTeam() is player.getTeam():

                # in free-for-all, killing yourself loses you a point
                if isinstance(self.getSession(),bs.FreeForAllSession):
                    newScore = player.getTeam().gameData['score'] - 1
                    if not self.settings['Allow Negative Scores']: newScore = max(0, newScore)
                    player.getTeam().gameData['score'] = newScore

                # in teams-mode it gives a point to the other team
                else:
                    bs.playSound(self._dingSound)
                    for team in self.teams:
                        if team is not killer.getTeam():
                            team.gameData['score'] += 1

            # killing someone on another team nets a kill
            else:
                killer.getTeam().gameData['score'] += 1
                bs.playSound(self._dingSound)
                # in FFA show our score since its hard to find on the scoreboard
                try: killer.actor.setScoreText(str(killer.getTeam().gameData['score'])+'/'+str(self._scoreToWin),color=killer.getTeam().color,flash=True)
                except Exception: pass

            self._updateScoreBoard()

            # if someone has won, set a timer to end shortly
            # (allows the dust to clear and draws to occur if deaths are close enough)
            if any(team.gameData['score'] >= self._scoreToWin for team in self.teams):
                bs.gameTimer(500,self.endGame)

        else: bs.TeamGameActivity.handleMessage(self,m)

    def _updateScoreBoard(self):
        for team in self.teams:
            self._scoreBoard.setTeamValue(team,team.gameData['score'],self._scoreToWin)

    def endGame(self):
        results = bs.TeamGameResults()
        for t in self.teams: results.setTeamScore(t,t.gameData['score'])
        self.end(results=results)

    def _nightSpawny(self):
        self.MythBrk = NightMod(position=(0, 0.05744967453, 0))
        
    def _DrunkPlayerCollide(self):
        self._whoisDrunk = {}
        playerNode = bs.getCollisionInfo('opposingNode')
        player = playerNode.getDelegate().getPlayer()
        self._whoisDrunk = player
        Pos1 = self._whoisDrunk.actor.node.positionCenter
        Posf2 = self._whoisDrunk.actor.node.positionForward
        self.cameraFlash(duration=10)
        velocity = (0,0,0)
        #print ('sarhos olan',self._whoisDrunk.getName())
        #mythbrk pos get pos
        bs.emitBGDynamics(position=(Pos1[0],Pos1[1],Pos1[2]),
                                      velocity=velocity,                                                                        #emitType= stickers,slime,tendrils,distortion
                                      count=random.randrange(0,2),scale=1.0,chunkType='slime',emitType= 'stickers') #slime,spark,splinter,ice,metal,rock,sweat
                                      
        direction = [Pos1[0]-Posf2[0],Posf2[1]-Pos1[1],Pos1[2]-Posf2[2]]
        direction[1] *= 10 
        t = 0.4
        
        
        star1 = bs.newNode("flash",
                           attrs={'position':(Pos1[0]+random.uniform(-t,t),Pos1[1]+random.uniform(-t,t),Pos1[2]+random.uniform(-t,t)),
                                  'size':0.1,
                                  'color':(2,0.8,0.4)})
        bs.gameTimer(60,star1.delete)
        
        star2 = bs.newNode("flash",
                           attrs={'position':(Pos1[0]+random.uniform(-t,t),Pos1[1]+random.uniform(-t,t),Pos1[2]+random.uniform(-t,t)),
                                  'size':0.06,
                                  'color':(1,0.8,0.4)})
        bs.gameTimer(60,star2.delete)
        
        star3 = bs.newNode("flash",
                           attrs={'position':(Pos1[0]+random.uniform(-t,t),Pos1[1]+random.uniform(-t,t),Pos1[2]+random.uniform(-t,t)),
                                  'size':0.02,
                                  'color':(1,0.8,2.4)})
        bs.gameTimer(60,star3.delete)
        
        star4 = bs.newNode("flash",
                           attrs={'position':(Pos1[0]+random.uniform(-t,t),Pos1[1]+random.uniform(-t,t),Pos1[2]+random.uniform(-t,t)),
                                  'size':0.03,
                                  'color':(2,0.8,0.4)})
        bs.gameTimer(60,star4.delete)
        
        star5 = bs.newNode("flash",
                           attrs={'position':(Pos1[0]+random.uniform(-t,t),Pos1[1]+random.uniform(-t,t),Pos1[2]+random.uniform(-t,t)),
                                  'size':0.01,
                                  'color':(2,0.8,0.4)})
        bs.gameTimer(60,star5.delete)



import bs           #Created By MythB # http://github.com/MythB
import random

def bsGetAPIVersion():
    # see bombsquadgame.com/apichanges
    return 4

def bsGetGames():
    return [PinyataGame]

def bsGetLevels():
    return [bs.Level('Pinyata', displayName='${GAME}', gameType=PinyataGame, settings={}, previewTexName='heart')]

class PinyataGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Pinyata'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName':'Score',
                'scoreType':'points'}
    
    @classmethod
    def getDescription(cls,sessionType):
        return 'Test'
	
	def getInstanceDescription(self):
		return 'TEST'

    # we're currently hard-coded for one map..
    @classmethod
    def getSupportedMaps(cls,sessionType):
        return ['Football Stadium']

    # we support teams, free-for-all, and co-op sessions
    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if (issubclass(sessionType,bs.CoopSession)
                        or issubclass(sessionType,bs.TeamsSession)
                        or issubclass(sessionType,bs.FreeForAllSession)) else False
    
    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)
        self._lastPlayerDeathTime = None
        self._scoreBoard = bs.ScoreBoard()
        self._eggModel = bs.getModel('shield')
        self._eggTex1 = bs.getTexture('eggTex1')
        self._eggTex2 = bs.getTexture('eggTex2')
        self._eggTex3 = bs.getTexture('eggTex3')
        self._collectSound = bs.getSound('powerup01')
        self._maxEggs = 1.0
        self._eggMaterial = bs.Material()
        self._eggMaterial.addActions(conditions=( ("weAreYoungerThan",100),'and',
                                                   ("theyHaveMaterial",bs.getSharedObject('objectMaterial')) ),
                                      actions=( ("modifyNodeCollision","collide",True) ) )
									  
        self._eggs = []

        
    # called when our game is transitioning in but not ready to start..
    # ..we can go ahead and set our music and whatnot
    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Marching')

    def onTeamJoin(self,team):
        team.gameData['score'] = 0
        if self.hasBegun(): self._updateScoreBoard()
        
    # called when our game actually starts
    def onBegin(self):

        # there's a player-wall on the tower-d level to prevent
        # players from getting up on the stairs.. we wanna kill that
        self.setupStandardPowerupDrops()
        bs.TeamGameActivity.onBegin(self)
        self._updateScoreBoard()
        self._updateTimer = bs.Timer(250,self._update,repeat=True)
        
        self._countdown = bs.OnScreenCountdown(3600, endCall=self.endGame)
        bs.gameTimer(4000, self._countdown.start)

        self._bots = bs.BotSet()
        # spawn evil bunny in co-op only
        if isinstance(self.getSession(),bs.CoopSession):
            self._spawnBigMommy()
        
    # overriding the default character spawning..
    def spawnPlayer(self,player):
        spaz = self.spawnPlayerSpaz(player)
        spaz.connectControlsToPlayer()

    def _spawnBigMommy(self):
        self._bots.spawnBot(bs.BunnyBot,pos=(5,4,5.8),spawnTime=1000)
        self._bots.spawnBot(bs.BunnyBot,pos=(2,4,-4),spawnTime=10000)
        self._bots.spawnBot(bs.BunnyBot,pos=(5,4,5.8),spawnTime=30000)

    def _onEggPlayerCollide(self):
        if not self.hasEnded():
            eggNode, playerNode = bs.getCollisionInfo('sourceNode','opposingNode')
            if eggNode is not None and playerNode is not None:
                egg = eggNode.getDelegate()
                spaz = playerNode.getDelegate()
                player = spaz.getPlayer() if hasattr(spaz,'getPlayer') else None
                if player is not None and player.exists() and egg is not None:
                    player.getTeam().gameData['score'] += 1
                    # displays a +1 (and adds to individual player score in teams mode)
                    self.scoreSet.playerScored(player,1,screenMessage=False)
                    if self._maxEggs < 5:
                        self._maxEggs += 1.0
                    elif self._maxEggs < 10:
                        self._maxEggs += 0.5
                    elif self._maxEggs < 30:
                        self._maxEggs += 0.3
                    self._updateScoreBoard()
                    bs.playSound(self._collectSound,0.5,position=egg.node.position)
                    # create a flash
                    light = bs.newNode('light',
                                       attrs={'position': eggNode.position,
                                              'heightAttenuated':False,
                                              'radius':0.1,
                                              'color':(1,1,0)})
                    bs.animate(light,'intensity',{0:0,100:1.0,200:0},loop=False)
                    bs.gameTimer(200,light.delete)
                    egg.handleMessage(bs.DieMessage())

        
    def _update(self):
        # misc. periodic updating..
        x = random.uniform(-7.1, 6.0)
        y = random.uniform(3.5, 3.5)
        z = random.uniform(-8.2, 3.7)
        
    # various high-level game events come through this method
    def handleMessage(self,m):

        # respawn dead players
        if isinstance(m,bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self,m) # augment standard
            self._aPlayerHasBeenKilled = True
            player = m.spaz.getPlayer()
            if not player.exists(): return
            self.scoreSet.playerLostSpaz(player)
            # respawn them shortly
            respawnTime = 2000+len(self.initialPlayerInfo)*1000
            player.gameData['respawnTimer'] = bs.Timer(respawnTime,bs.Call(self.spawnPlayerIfExists,player))
            player.gameData['respawnIcon'] = bs.RespawnIcon(player,respawnTime)

        # whenever our evil bunny dies, respawn him and spew some eggs
        elif isinstance(m,bs.SpazBotDeathMessage):
            pt = m.badGuy.node.position
            for i in range(54):
                s = 0.4
                self._eggs.append(Egg(position=(pt[0]+random.uniform(-s,s),
                                                pt[1]+random.uniform(-s,s),
                                                pt[2]+random.uniform(-s,s))))


    def _updateScoreBoard(self):
        for team in self.teams:
            self._scoreBoard.setTeamValue(team,team.gameData['score'])


    def endGame(self):
        results = bs.TeamGameResults()
        for team in self.teams:
            results.setTeamScore(team,team.gameData['score'])
        self.end(results)

class Egg(bs.Actor):

    def __init__(self, position=(0,1,0)):
        bs.Actor.__init__(self)

        activity = self.getActivity()
        
        # spawn just above the provided point
        self._spawnPos = (position[0], position[1]+1.0, position[2])
        self.node = bs.newNode("prop",
                               attrs={'model': activity._eggModel,
                                      'colorTexture': (activity._eggTex1,activity._eggTex2,activity._eggTex3)[random.randrange(3)],
                                      'body':'sphere',
                                      'reflection':'soft',
                                      'modelScale':0.27,
									  'bodyScale': 2.0,
									  'modelScale':0.5,
									  'density':0.075,
                                      'reflectionScale':[0.15],
                                      'shadowSize': 0.6,
                                      'position':self._spawnPos,
                                      'materials': [bs.getSharedObject('objectMaterial'),activity._eggMaterial]
                                      },
                               delegate=self)

    def handleMessage(self,m):
        if isinstance(m,bs.DieMessage):
            self.node.delete()
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())
        elif isinstance(m,bs.HitMessage):
            self.node.handleMessage("impulse",m.pos[0],m.pos[1],m.pos[2],
                                    m.velocity[0],m.velocity[1],m.velocity[2],
                                    1.0*m.magnitude,1.0*m.velocityMagnitude,m.radius,0,
                                    m.forceDirection[0],m.forceDirection[1],m.forceDirection[2])
        else:
            bs.Actor.handleMessage(self,m)
        

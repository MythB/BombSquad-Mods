import bs        #Created By MythB # 2016 # http://github.com/MythB
import random

def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [BigBallGame]

class BallDeathMessage(object):
    """A ball has died."""
    def __init__(self,ball):
        self.ball = ball

#goalpost
class FlagKale(bs.Actor):
    def __init__(self,position=(0,2.5,0),color=(1,1,1)):
        bs.Actor.__init__(self)

        activity = self.getActivity()
        
        self.node = bs.newNode("flag",
                               attrs={'position':(position[0],position[1]+0.75,position[2]),
                                      'colorTexture':activity._flagKaleTex,
                                      'color':color,
                                      'materials':[bs.getSharedObject('objectMaterial'),activity._kaleMaterial]},
                               delegate=self)

    def handleMessage(self,m):
        self._handleMessageSanityCheck()
        if isinstance(m,bs.DieMessage):
            if self.node.exists():
                self.node.delete()
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage(how='fall'))
        else:
            bs.Actor.handleMessage(self,m)

#We will play with this ball
class Ball(bs.Actor):

    def __init__(self,position=(0,2.5,0)):
        bs.Actor.__init__(self)

        activity = self.getActivity()
        
        # spawn just above the provided point
        self._spawnPos = (position[0],position[1]+1.0,position[2])
        self.lastPlayersToTouch = {}
        self.node = bs.newNode("prop",
                               attrs={'model': activity._ballModel,
                                      'colorTexture': activity._ballTex,
                                      'body':'sphere',
                                      'reflection':'soft',
                                      'bodyScale': 4.0,
                                      'modelScale':1.0,
                                      'density':0.020,
                                      'reflectionScale':[0.20],
                                      'shadowSize': 0.8,
                                      'isAreaOfInterest':True,
                                      'position':self._spawnPos,
                                      'materials': [bs.getSharedObject('objectMaterial'),activity._ballMaterial]
                                      },
                               delegate=self)

    def handleMessage(self,m):
        if isinstance(m,bs.DieMessage):
            self.node.delete()
            activity = self._activity()
            if activity and not m.immediate:
                activity.handleMessage(BallDeathMessage(self))

        # if we go out of bounds, move back to where we started...
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.node.position = self._spawnPos

        elif isinstance(m,bs.HitMessage):
            self.node.handleMessage("impulse",m.pos[0],m.pos[1],m.pos[2],
                                    m.velocity[0],m.velocity[1],m.velocity[2],
                                    1.0*m.magnitude,1.0*m.velocityMagnitude,m.radius,0,
                                    m.forceDirection[0],m.forceDirection[1],m.forceDirection[2])

            # if this hit came from a player, log them as the last to touch us
            if m.sourcePlayer is not None:
                activity = self._activity()
                if activity:
                    if m.sourcePlayer in activity.players:
                        self.lastPlayersToTouch[m.sourcePlayer.getTeam().getID()] = m.sourcePlayer
        else:
            bs.Actor.handleMessage(self,m)

#for night mode: using a actor with large shadow and little model scale. Better then tint i think, players and objects more visible
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

class BigBallGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Big Ball'

    @classmethod
    def getDescription(cls,sessionType):
        return 'Score some goals.\nFlags are goalposts.\nScored team players getting boxing gloves,\nNon-scored team players getting shield.\nYou can set Night Mode !!'

    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if issubclass(sessionType,bs.TeamsSession) else False

    @classmethod
    def getSupportedMaps(cls,sessionType):
        return bs.getMapsSupportingPlayType('football')

    @classmethod
    def getSettings(cls,sessionType):
        return [("Score to Win",{'minValue':1,'default':10,'increment':1}),
                ("Time Limit",{'choices':[('None',0),('1 Minute',60),
                                          ('2 Minutes',120),('5 Minutes',300),
                                          ('10 Minutes',600),('20 Minutes',1200)],'default':0}),
                ("Respawn Times",{'choices':[('Short',0.75),('Normal',1.50),('Long',2.25)],'default':1.50}),
                ('Night Mode', {'default': False})]

    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)
        self._scoreBoard = bs.ScoreBoard()
        
        self._cheerSound = bs.getSound("cheer")
        self._chantSound = bs.getSound("crowdChant")
        self._scoreSound = bs.getSound("score")
        self._swipSound = bs.getSound("swip")
        self._whistleSound = bs.getSound("refWhistle")
        self._ballModel = bs.getModel("shield")
        self._ballTex = bs.getTexture("eggTex1")
        self._ballSound = bs.getSound("impactMedium2")
        self._flagKaleTex = bs.getTexture("star")
        self._kaleSound = bs.getSound("metalHit")
        self._nightModel = bs.getModel("shield")
        self._nightTex = bs.getTexture("black")

        self._kaleMaterial = bs.Material()
        #add friction to flags for standing our position (as far as)
        self._kaleMaterial.addActions(conditions=("theyHaveMaterial",bs.getSharedObject('footingMaterial')),
                                         actions=( ("modifyPartCollision","friction",9999.5)))
        self._kaleMaterial.addActions(conditions=("theyHaveMaterial",bs.getSharedObject('pickupMaterial')),
                                      actions=( ("modifyPartCollision","collide",False) ) )
        self._kaleMaterial.addActions(conditions=( ("weAreYoungerThan",100),'and',
                                                   ("theyHaveMaterial",bs.getSharedObject('objectMaterial')) ),
                                      actions=( ("modifyNodeCollision","collide",False) ) )
        #dont collide with bombs #FIXME "standing"
        self._kaleMaterial.addActions(conditions=("theyHaveMaterial",bs.Bomb.getFactory().blastMaterial),
                                      actions=(("modifyPartCollision","collide",False),
                                               ("modifyPartCollision","physical",False)))
        self._kaleMaterial.addActions(conditions=("theyHaveMaterial",bs.Bomb.getFactory().bombMaterial),
                                      actions=(("modifyPartCollision","collide",False),
                                               ("modifyPartCollision","physical",False)))
        self._kaleMaterial.addActions(
            conditions=('theyHaveMaterial',bs.getSharedObject('objectMaterial')),
            actions=(('impactSound',self._kaleSound,2,5)))
        #we dont wanna hit the night so
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


        self._ballMaterial = bs.Material()
        self._ballMaterial.addActions(actions=( ("modifyPartCollision","friction",0.75)))
        self._ballMaterial.addActions(conditions=("theyHaveMaterial",bs.getSharedObject('pickupMaterial')),
                                      actions=( ("modifyPartCollision","collide",False) ) )
        self._ballMaterial.addActions(conditions=( ("weAreYoungerThan",100),'and',
                                                 ("theyHaveMaterial",bs.getSharedObject('objectMaterial')) ),
                                      actions=( ("modifyNodeCollision","collide",False) ) )
        self._ballMaterial.addActions(conditions=("theyHaveMaterial",bs.getSharedObject('footingMaterial')),
                                      actions=(("impactSound",self._ballSound,2,0.8)))
        # keep track of which player last touched the ball
        self._ballMaterial.addActions(conditions=("theyHaveMaterial",bs.getSharedObject('playerMaterial')),
                                      actions=(("call","atConnect",self._handleBallPlayerCollide),))
        # we want the ball to kill powerups; not get stopped by them
        self._ballMaterial.addActions(conditions=("theyHaveMaterial",bs.Powerup.getFactory().powerupMaterial),
                                      actions=(("modifyPartCollision","physical",False),
                                               ("message","theirNode","atConnect",bs.DieMessage())))

        self._scoreRegionMaterial = bs.Material()
        self._scoreRegionMaterial.addActions(conditions=("theyHaveMaterial",self._ballMaterial),
                                             actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect",self._handleScore)))

    def getInstanceDescription(self):
        if self.settings['Score to Win'] == 1: return 'Score a goal.'
        else: return ('Score ${ARG1} goals.',self.settings['Score to Win'])

    def getInstanceScoreBoardDescription(self):
        if self.settings['Score to Win'] == 1: return 'score a goal'
        else: return ('score ${ARG1} goals',self.settings['Score to Win'])

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Hockey')

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)

        self.setupStandardTimeLimit(self.settings['Time Limit'])
        self.setupStandardPowerupDrops(enableTNT=False)

        self._ballSpawnPos = self.getMap().getFlagPosition(None)
        self._spawnBall()
        #for night mode we need night actor. And same goodies for nigh mode
        if self.settings['Night Mode']: self._nightSpawny(),self._flagKaleFlash()

        # set up the two score regions
        defs = self.getMap().defs
        self._scoreRegions = []
        self._scoreRegions.append(bs.NodeActor(bs.newNode("region",
                                                          attrs={'position':(13.75, 0.85744967453, 0.1095578275),
                                                                 'type':"box",
                                                                'scale': (1.05,1.1,3.8),
                                                                 'materials':[self._scoreRegionMaterial]})))
        
        self._scoreRegions.append(bs.NodeActor(bs.newNode("region",
                                                          attrs={'position':(-13.55, 0.85744967453, 0.1095578275),
                                                                 'type':"box",
                                                                 'scale': (1.05,1.1,3.8),
                                                                 'materials':[self._scoreRegionMaterial]})))
        self._updateScoreBoard()

        bs.playSound(self._chantSound)

    def onTeamJoin(self,team):
        team.gameData['score'] = 0
        self._updateScoreBoard()

    def _handleBallPlayerCollide(self):
        try:
            ballNode,playerNode = bs.getCollisionInfo('sourceNode','opposingNode')
            ball = ballNode.getDelegate()
            player = playerNode.getDelegate().getPlayer()
        except Exception: player = ball = None

        if player is not None and player.exists() and ball is not None: ball.lastPlayersToTouch[player.getTeam().getID()] = player

    def _killBall(self):
        self._ball = None

    def _handleScore(self):
        """ a point has been scored """

        # our ball might stick around for a second or two
        # we dont want it to be able to score again
        if self._ball.scored: return

        region = bs.getCollisionInfo("sourceNode")
        for i in range(len(self._scoreRegions)):
            if region == self._scoreRegions[i].node:
                break;

        scoringTeam = None
        for team in self.teams:
            if team.getID() == i:
                scoringTeam = team
                team.gameData['score'] += 1

                # tell scored team players to celebrate and give them to boxing gloves
                for player in team.players:
                    try: player.actor.node.handleMessage('celebrate',2000) or player.actor.node.handleMessage(bs.PowerupMessage('punch'))
                    except Exception: pass

                # if weve got the player from the scoring team that last touched us, give them points
                if scoringTeam.getID() in self._ball.lastPlayersToTouch and self._ball.lastPlayersToTouch[scoringTeam.getID()].exists():
                    self.scoreSet.playerScored(self._ball.lastPlayersToTouch[scoringTeam.getID()],100,bigMessage=True)

                # end game if we won
                if team.gameData['score'] >= self.settings['Score to Win']:
                    bs.gameTimer(1250,self.endGame)	

        scoringTeam = None
        for team in self.teams:
            if not team.getID() == i:
                scoringTeam = team
                team.gameData['score'] += 0

                # give non-scored team players to shield for balance
                for player in team.players:
                    try: player.actor.node.handleMessage(bs.PowerupMessage('shield'))
                    except Exception: pass
                    

        bs.playSound(self._scoreSound)
        bs.playSound(self._cheerSound)

        self._ball.scored = True

        # kill the ball (it'll respawn itself shortly)
        bs.gameTimer(1000,self._killBall)

        light = bs.newNode('light',
                           attrs={'position': bs.getCollisionInfo('position'),
                                  'heightAttenuated':False,
                                  'color': (1,0,0)})
        bs.animate(light,'intensity',{0:0,500:1,1000:0},loop=True)
        bs.gameTimer(1000,light.delete)

        self.cameraFlash(duration=10)
        self._updateScoreBoard()
        
        #pretty celebrate
        if scoringTeam.getID() == 1:
                bs.emitBGDynamics(position=(12.66, 0.03986567039, 2.075),
                                  velocity=(0,0,0),
                                  count=random.randrange(20,70),scale=1.0,chunkType='spark')
                bs.emitBGDynamics(position=(12.66, 0.03986567039, -2.075),
                                  velocity=(0,0,0),
                                  count=random.randrange(20,70),scale=1.0,chunkType='spark')
                                  
        if scoringTeam.getID() == 0:
                bs.emitBGDynamics(position=(-12.45, 0.05744967453, -2.075),
                                  velocity=(0,0,0),
                                  count=random.randrange(20,70),scale=1.0,chunkType='spark')
                bs.emitBGDynamics(position=(-12.45, 0.05744967453, 2.075),
                                  velocity=(0,0,0),
                                  count=random.randrange(20,70),scale=1.0,chunkType='spark')

    def endGame(self):
        results = bs.TeamGameResults()
        for t in self.teams: results.setTeamScore(t,t.gameData['score'])
        self.end(results=results)

    def _updateScoreBoard(self):
        """ update scoreboard and check for winners """
        winScore = self.settings['Score to Win']
        for team in self.teams:
            self._scoreBoard.setTeamValue(team,team.gameData['score'],winScore)

    def handleMessage(self,m):

        # respawn dead players if they're still in the game
        if isinstance(m,bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self,m) # augment standard behavior
            self.respawnPlayer(m.spaz.getPlayer())
        # respawn dead balls
        elif isinstance(m,BallDeathMessage):
            if not self.hasEnded():
                bs.gameTimer(3000,self._spawnBall)
        else:
            bs.TeamGameActivity.handleMessage(self,m)

    def _nightSpawny(self):
        self.MythBrk = NightMod(position=(0, 0.05744967453, 0))

    #spawn some goodies on nightmode for pretty visuals
    def _flagKaleFlash(self):
        #flags positions
        kale1 = (-12.45, 0.05744967453, -2.075)
        kale2 = (-12.45, 0.05744967453, 2.075)
        kale3 = (12.66, 0.03986567039, 2.075)
        kale4 = (12.66, 0.03986567039, -2.075)

        flash = bs.newNode("light",
                                   attrs={'position':kale1,
                                          'radius':0.15,
                                          'color':(1.0,1.0,0.7)})

        flash = bs.newNode("light",
                                   attrs={'position':kale2,
                                          'radius':0.15,
                                          'color':(1.0,1.0,0.7)})

        flash = bs.newNode("light",
                                   attrs={'position':kale3,
                                          'radius':0.15,
                                          'color':(0.7,1.0,1.0)})

        flash = bs.newNode("light",
                                   attrs={'position':kale4,
                                          'radius':0.15,
                                          'color':(0.7,1.0,1.0)})
    #flags positions
    def _flagKalesSpawn(self):
        for team in self.teams:
            if team.getID() == 0:
               _colorTeam0 = team.color
            if team.getID() == 1:
               _colorTeam1 = team.color

        self._MythB = FlagKale(position=(-12.45, 0.05744967453, -2.075),color=_colorTeam0)
        self._MythB2 =FlagKale(position=(-12.45, 0.05744967453, 2.075),color=_colorTeam0)
        self._MythB3 =FlagKale(position=(12.66, 0.03986567039, 2.075),color=_colorTeam1)
        self._MythB4 =FlagKale(position=(12.66, 0.03986567039, -2.075),color=_colorTeam1)

    def _flashBallSpawn(self):
        light = bs.newNode('light',
                           attrs={'position': self._ballSpawnPos,
                                  'heightAttenuated':False,
                                  'color': (0.8,0.2,0.8)})
        bs.animate(light,'intensity',{0:0,250:1,500:0},loop=True)
        bs.gameTimer(1000,light.delete)

    def _spawnBall(self):
        bs.playSound(self._swipSound)
        bs.playSound(self._whistleSound)
        #this is here coz flags can move anywise so we wanna spawn them repeatedly #FIXME if you figure out
        self._flagKalesSpawn()
        self._flashBallSpawn()

        self._ball = Ball(position=self._ballSpawnPos)
        self._ball.scored = False
        self._ball.lastHoldingPlayer = None
        self._ball.light = bs.newNode('light',
                                      owner=self._ball.node,
                                      attrs={'intensity':0.3,
                                             'heightAttenuated':False,
                                             'radius':0.2,
                                             'color': (0.9,0.2,0.9)})
        self._ball.node.connectAttr('position',self._ball.light,'position')


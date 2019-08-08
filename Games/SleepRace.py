import bs        #Created By MythB # http://github.com/MythB
import random
import bsUtils


def bsGetAPIVersion():
    # see bombsquadgame.com/apichanges
    return 4


def bsGetGames():
    return [SleepRaceGame]


class RaceRegion(bs.Actor):
    def __init__(self, pt, index):
        bs.Actor.__init__(self)
        activity = self.getActivity()
        self._pt = pt
        self._index = index
        self.node = bs.newNode(
            "region", owner=self, delegate=self,
            attrs={'position': pt[: 3],
                   'scale': (pt[3] * 2.0, pt[4] * 2.0, pt[5] * 2.0),
                   'type': "box", 'materials': [activity._raceRegionMaterial]})


class SleepRaceGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Sleep Race'

    @classmethod
    def getDescription(cls, sessionType):
        return 'Dont sleep too much!'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName': 'Time',
                'lowerIsBetter': True,
                'scoreType': 'milliseconds'}

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if(
            issubclass(sessionType, bs.TeamsSession)
            or issubclass(sessionType, bs.FreeForAllSession)) else False

    @classmethod
    def getSupportedMaps(cls, sessionType):
        return bs.getMapsSupportingPlayType("race")

    @classmethod
    def getSettings(cls, sessionType):
        settings = [("Laps", {'minValue': 1, "default": 3, "increment": 1}),
                    ("Time Limit", {'choices': [('None', 0),
                                                ('1 Minute', 60),
                                                ('2 Minutes', 120),
                                                ('5 Minutes', 300),
                                                ('10 Minutes', 600),
                                                ('20 Minutes', 1200)],
                                    'default':0}),
                    ("Mine Spawning", {'choices': [('No Mines', 0),
                                                   ('8 Seconds', 8000),
                                                   ('4 Seconds', 4000),
                                                   ('2 Seconds', 2000)],
                                       'default':4000}),
                    ("Bomb Spawning", {'choices': [('None', 0),
                                                   ('8 Seconds', 8000),
                                                   ('4 Seconds', 4000),
                                                   ('2 Seconds', 2000),
                                                   ('1 Second', 1000)],
                                       'default':2000}),
                    ("Epic Mode", {'default': False})]

        if issubclass(sessionType, bs.TeamsSession):
            settings.append(("Entire Team Must Finish", {'default': False}))
        return settings

    def __init__(self, settings):
        self._raceStarted = False
        bs.TeamGameActivity.__init__(self, settings)
        self._scoreBoard = bs.ScoreBoard()
        if self.settings['Epic Mode']:
            self._isSlowMotion = True
        self._scoreSound = bs.getSound("score")
        self._swipSound = bs.getSound("swip")
        self._lastTeamTime = None
        self._frontRaceRegion = None

    def getInstanceDescription(self):
        if isinstance(
                self.getSession(),
                bs.TeamsSession) and self.settings.get(
                'Entire Team Must Finish', False):
            tStr = ' Your entire team has to finish.'
        else:
            tStr = ''

        if self.settings['Laps'] > 1:
            s = ('Run ${ARG1} laps.'+tStr, self.settings['Laps'])
        else:
            s = 'Run 1 lap.'+tStr
        return s

    def getInstanceScoreBoardDescription(self):
        if self.settings['Laps'] > 1:
            s = ('run ${ARG1} laps', self.settings['Laps'])
        else:
            s = 'run 1 lap'
        return s

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(
            self, music='Epic Race' if self.settings['Epic Mode'] else 'Race')

        self._nubTex = bs.getTexture('nub')
        self._beep1Sound = bs.getSound('raceBeep1')
        self._beep2Sound = bs.getSound('raceBeep2')

        pts = self.getMap().getDefPoints('racePoint')

        m = self._raceRegionMaterial = bs.Material()
        m.addActions(
            conditions=("theyHaveMaterial",
                        bs.getSharedObject('playerMaterial')),
            actions=(("modifyPartCollision", "collide", True),
                     ("modifyPartCollision", "physical", False),
                     ("call", "atConnect", self._handleRacePointCollide)))

        self._regions = []
        for pt in pts:
            self._regions.append(RaceRegion(pt, len(self._regions)))

    def _flashPlayer(self, player, scale):
        pos = player.actor.node.position
        light = bs.newNode('light',
                           attrs={'position': pos,
                                  'color': (1, 1, 0),
                                  'heightAttenuated': False,
                                  'radius': 0.4})
        bs.gameTimer(500, light.delete)
        bs.animate(light, 'intensity', {0: 0, 100: 1.0*scale, 500: 0})

    def _handleRacePointCollide(self):

        regionNode, playerNode = bs.getCollisionInfo(
            'sourceNode', 'opposingNode')
        try:
            player = playerNode.getDelegate().getPlayer()
        except Exception:
            player = None
        region = regionNode.getDelegate()
        if player is None or not player.exists() or region is None:
            return

        lastRegion = player.gameData['lastRegion']
        thisRegion = region._index

        if lastRegion != thisRegion:

            # if a player tries to skip regions, smite them
            # ..allow a one region leeway though (its plausable players can get
            # blown over a region, etc)
            if thisRegion > lastRegion + 2:
                if player.isAlive():
                    player.actor.handleMessage(bs.DieMessage())
                    bs.screenMessage(
                        bs.Lstr(translate=(
                            'statements',
                            "Killing ${NAME} for skipping part of the track!"),
                            subs=[('${NAME}', player.getName(full=True))]),
                        color=(1, 0, 0))
            else:
                # if this player is in first, note that this is the
                # front-most race-point
                if player.gameData['rank'] == 0:
                    self._frontRaceRegion = thisRegion

                player.gameData['lastRegion'] = thisRegion
                if lastRegion >= len(self._regions)-2 and thisRegion == 0:
                    team = player.getTeam()
                    player.gameData['lap'] = min(
                        self.settings['Laps'],
                        player.gameData['lap'] + 1)

                    # in teams mode with all-must-finish on, the team lap
                    # value is the min of all team players
                    # ..otherwise its the max
                    if isinstance(
                            self.getSession(),
                            bs.TeamsSession) and self.settings.get(
                            'Entire Team Must Finish'):
                        team.gameData['lap'] = min(
                            [p.gameData['lap'] for p in team.players])
                    else:
                        team.gameData['lap'] = max(
                            [p.gameData['lap'] for p in team.players])

                    # a player is finishing
                    if player.gameData['lap'] == self.settings['Laps']:

                        # in teams mode, hand out points based on the order
                        # players come in
                        if isinstance(self.getSession(), bs.TeamsSession):
                            if self._teamFinishPts > 0:
                                self.scoreSet.playerScored(
                                    player, self._teamFinishPts,
                                    screenMessage=False)
                            self._teamFinishPts -= 25

                        # flash where the player is
                        self._flashPlayer(player, 1.0)
                        player.gameData['finished'] = True
                        player.actor.handleMessage(
                            bs.DieMessage(immediate=True))

                        # makes sure noone behind them passes them in rank
                        # while finishing..
                        player.gameData['distance'] = 9999.0

                        # if the whole team has finished the race..
                        if team.gameData['lap'] == self.settings['Laps']:
                            bs.playSound(self._scoreSound)
                            player.getTeam().gameData['finished'] = True
                            self._lastTeamTime = player.getTeam(
                            ).gameData['time'] = \
                                bs.getGameTime()-self._timer.getStartTime()
                            self._checkEndGame()

                        # team has yet to finish..
                        else:
                            bs.playSound(self._swipSound)

                    # they've just finished a lap but not the race..
                    else:
                        bs.playSound(self._swipSound)
                        self._flashPlayer(player, 0.3)

                        # print their lap number over their head..
                        try:
                            m = bs.newNode('math', owner=player.actor.node,
                                           attrs={'input1': (0, 1.9, 0),
                                                  'operation': 'add'})
                            player.actor.node.connectAttr(
                                'torsoPosition', m, 'input2')
                            t = bs.newNode('text', owner=m, attrs={
                                'text': bs.Lstr(
                                    resource='lapNumberText',
                                    subs=[('${CURRENT}',
                                           str(player.gameData['lap']+1)),
                                          ('${TOTAL}',
                                           str(self.settings['Laps']))]),
                                'inWorld': True,
                                'color': (1, 1, 0, 1),
                                'scale': 0.015,
                                'hAlign': 'center'})
                            m.connectAttr('output', t, 'position')
                            bs.animate(
                                t, 'scale',
                                {0: 0, 200: 0.019, 2000: 0.019, 2200: 0})
                            bs.gameTimer(2300, m.delete)
                        except Exception, e:
                            print 'Exception printing lap:', e

    def onTeamJoin(self, team):
        team.gameData['time'] = None
        team.gameData['lap'] = 0
        team.gameData['finished'] = False
        self._updateScoreBoard()

    def onPlayerJoin(self, player):
        player.gameData['lastRegion'] = 0
        player.gameData['lap'] = 0
        player.gameData['distance'] = 0.0
        player.gameData['finished'] = False
        player.gameData['rank'] = None
        bs.TeamGameActivity.onPlayerJoin(self, player)

    def onPlayerLeave(self, player):
        bs.TeamGameActivity.onPlayerLeave(self, player)

        # a player leaving disqualifies the team if 'Entire Team Must Finish'
        # is on (otherwise in teams mode everyone could just leave except the
        # leading player to win)
        if isinstance(self.getSession(),
                      bs.TeamsSession) and self.settings.get(
                'Entire Team Must Finish'):
            # FIXME translate this
            bs.screenMessage(
                bs.Lstr(
                    translate=(
                        'statements',
                        '${TEAM} is disqualified because ${PLAYER} left'),
                    subs=[('${TEAM}', player.getTeam().name),
                          ('${PLAYER}', player.getName(full=True))]),
                color=(1, 1, 0))
            player.getTeam().gameData['finished'] = True
            player.getTeam().gameData['time'] = None
            player.getTeam().gameData['lap'] = 0
            bs.playSound(bs.getSound("boo"))
            for player in player.getTeam().players:
                player.gameData['lap'] = 0
                player.gameData['finished'] = True
                try:
                    player.actor.handleMessage(bs.DieMessage())
                except Exception:
                    pass

        # delay by one tick so team/player lists will be updated
        bs.gameTimer(1, self._checkEndGame)

    def _updateScoreBoard(self):
        for team in self.teams:
            distances = [player.gameData['distance'] for player in team.players]
            if len(distances) == 0:
                teamDist = 0
            else:
                if isinstance(
                        self.getSession(),
                        bs.TeamsSession) and self.settings.get(
                        'Entire Team Must Finish'):
                    teamDist = min(distances)
                else:
                    teamDist = max(distances)
            self._scoreBoard.setTeamValue(
                team, teamDist, self.settings['Laps'],
                flash=(teamDist >= float(self.settings['Laps'])),
                showValue=False)

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self.setupStandardTimeLimit(self.settings['Time Limit'])
        self.setupStandardPowerupDrops()
        self._teamFinishPts = 100

        # throw a timer up on-screen
        self._timeText = bs.NodeActor(
            bs.newNode(
                'text',
                attrs={'vAttach': 'top', 'hAttach': 'center',
                       'hAlign': 'center', 'color': (1, 1, 0.5, 1),
                       'flatness': 0.5, 'shadow': 0.5, 'position': (0, -50),
                       'scale': 1.4, 'text': ''}))
        self._timer = bs.OnScreenTimer()

        if self.settings['Mine Spawning'] != 0:
            self._raceMines = [
                {'point': p, 'mine': None}
                for p in self.getMap().getDefPoints('raceMine')]
            if len(self._raceMines) > 0:
                self._raceMineTimer = bs.Timer(
                    self.settings['Mine Spawning'],
                    self._updateRaceMine, repeat=True)

        self._scoreBoardTimer = bs.Timer(
            250, self._updateScoreBoard, repeat=True)
        self._playerOrderUpdateTimer = bs.Timer(
            250, self._updatePlayerOrder, repeat=True)

        if self._isSlowMotion:
            tScale = 0.4
            lightY = 50
        else:
            tScale = 1.0
            lightY = 150
        lStart = int(7100*tScale)
        inc = int(1250*tScale)

        bs.gameTimer(lStart, self._doLight1)
        bs.gameTimer(lStart+inc, self._doLight2)
        bs.gameTimer(lStart+2*inc, self._doLight3)
        bs.gameTimer(lStart+3*inc, self._startRace)

        self._startLights = []
        for i in range(4):
            l = bs.newNode('image',
                           attrs={'texture': bs.getTexture('nub'),
                                  'opacity': 1.0,
                                  'absoluteScale': True,
                                  'position': (-75+i*50, lightY),
                                  'scale': (50, 50),
                                  'attach': 'center'})
            bs.animate(
                l, 'opacity',
                {4000 * tScale: 0, 5000 * tScale: 1.0, 12000 * tScale: 1.0,
                 12500 * tScale: 0.0})
            bs.gameTimer(int(13000*tScale), l.delete)
            self._startLights.append(l)

        self._startLights[0].color = (0.2, 0, 0)
        self._startLights[1].color = (0.2, 0, 0)
        self._startLights[2].color = (0.2, 0.05, 0)
        self._startLights[3].color = (0.0, 0.3, 0)
        self._organizer()

    def _organizer(self):
          self.blablabla = bs.Timer(random.randrange(1000,15000),bs.Call(self._doNight)) #do night
        
    def _doNight(self):
           self._isSleep = False
           self.tint = bs.getSharedObject('globals').tint
           bsUtils.animateArray(bs.getSharedObject('globals'),"tint",3,{0:self.tint,1000:(0.3,0.3,0.6)})
           bs.playSound(bs.getSound('shieldUp'),volume = 10,position = (0,10,0))
           self._repeaterOne = bs.Timer(450,bs.WeakCall(self._doSleep),repeat=True) #shutdown our spazs
           self._repeaterTwo = bs.Timer(random.randrange(1000,10000),bs.WeakCall(self._doWakeUp)) #wakeup our spazs
    def _doSleep(self):
        if self._isSleep == False:
            for i in bs.getActivity().players:
                try:
                    if i.actor.exists() and i.actor.isAlive():
                       i.actor.node.handleMessage("knockout",3000)
                       zZZText = bsUtils.PopupText("Z",color=(1,1,1),
                                          scale=0.7,
                                          randomOffset=0.2,
                                          offset=(0,-1,0),
                                          position=(i.actor.node.position[0],i.actor.node.position[1]-1.2,i.actor.node.position[2])).autoRetain()
                except Exception as e:
                    print ('SleepRace : _doSleep : in try block : Exception : '), e
    def _doWakeUp(self):
        self._isSleep = True
        def Delay(): # delay for sync coz our spazs are very lazy
            bs.playSound(bs.getSound('healthPowerup'),volume = 10,position = (0,10,0))
            if self.getMap().getName() == 'Lake Frigid':
                 self.tint = bs.getSharedObject('globals').tint
                 bsUtils.animateArray(bs.getSharedObject('globals'),"tint",3,{0:self.tint,1000:(1,1,1)})
            elif self.getMap().getName() == 'Big G':
                 self.tint = bs.getSharedObject('globals').tint
                 bsUtils.animateArray(bs.getSharedObject('globals'),"tint",3,{0:self.tint,1000:(1.1,1.2,1.3)})
            self._organizer()
        bs.gameTimer(1500,Delay)
        
        
    def _doLight1(self):
        self._startLights[0].color = (1.0, 0, 0)
        bs.playSound(self._beep1Sound)

    def _doLight2(self):
        self._startLights[1].color = (1.0, 0, 0)
        bs.playSound(self._beep1Sound)

    def _doLight3(self):
        self._startLights[2].color = (1.0, 0.3, 0)
        bs.playSound(self._beep1Sound)

    def _startRace(self):
        self._startLights[3].color = (0.0, 1.0, 0)
        bs.playSound(self._beep2Sound)
        for player in self.players:
            if player.actor is not None:
                try:
                    player.actor.connectControlsToPlayer()
                except Exception, e:
                    print 'Exception in race player connects:', e
        self._timer.start()

        if self.settings['Bomb Spawning'] != 0:
            self._bombSpawnTimer = bs.Timer(
                self.settings['Bomb Spawning'],
                self._spawnBomb, repeat=True)

        self._raceStarted = True

    def _updatePlayerOrder(self):

        # calc all player distances
        for player in self.players:
            try:
                pos = bs.Vector(*player.actor.node.position)
            except Exception:
                pos = None
            if pos is not None:
                rIndex = player.gameData['lastRegion']
                r1 = self._regions[rIndex]
                r1Pt = bs.Vector(*r1._pt[:3])
                r2 = self._regions[0] if rIndex == len(
                    self._regions)-1 else self._regions[rIndex+1]
                r2Pt = bs.Vector(*r2._pt[:3])
                r1Dist = (pos-r1Pt).length()
                r2Dist = (pos-r2Pt).length()
                amt = 1.0-(r2Dist/(r2Pt-r1Pt).length())
                amt = player.gameData['lap'] + (
                    rIndex+amt) * (1.0/len(self._regions))
                player.gameData['distance'] = amt

        # sort players by distance and update their ranks
        pList = [[player.gameData['distance'], player]
                 for player in self.players]
        pList.sort(reverse=True)
        for i, p in enumerate(pList):
            try:
                p[1].gameData['rank'] = i
                if p[1].actor is not None:
                    n = p[1].actor.distanceTxt
                    if n.exists():
                        n.text = str(i+1) if p[1].isAlive() else ''
            except Exception:
                bs.printException('error updating player orders')

    def _spawnBomb(self):
        if self._frontRaceRegion is None:
            return
        region = (self._frontRaceRegion+(3)) % len(self._regions)
        #print 'WOULD SPAWN BOMB AT',bs.getGameTime(),'AT REGION',region
        pt = self._regions[region]._pt
        # dont use the full region so we're less likely to spawn off a cliff
        regionScale = 0.8
        xRange = ((-0.5, 0.5) if pt[3] == 0
                  else (-regionScale*pt[3], regionScale*pt[3]))
        zRange = ((-0.5, 0.5) if pt[5] == 0
                  else (-regionScale*pt[5], regionScale*pt[5]))
        pt = (pt[0]+random.uniform(*xRange),
              pt[1]+1.0, pt[2]+random.uniform(*zRange))
        bs.gameTimer(
            random.randrange(2000),
            bs.WeakCall(self._spawnBombAtPt, pt))

    def _spawnBombAtPt(self, pt):
        if self.hasEnded():
            return
        bs.Bomb(position=pt, bombType='normal').autoRetain()

    def _makeMine(self, i):
        m = self._raceMines[i]
        m['mine'] = bs.Bomb(position=m['point'][:3], bombType='landMine')
        m['mine'].arm()

    def _flashMine(self, i):
        m = self._raceMines[i]
        light = bs.newNode("light",
                           attrs={'position': m['point'][:3],
                                  'color': (1, 0.2, 0.2),
                                  'radius': 0.1,
                                  'heightAttenuated': False})
        bs.animate(light, "intensity", {0: 0, 100: 1.0, 200: 0}, loop=True)
        bs.gameTimer(1000, light.delete)

    def _updateRaceMine(self):
        for i in range(3):
            mIndex = random.randrange(len(self._raceMines))
            m = self._raceMines[mIndex]
            if m['mine'] is None or not m['mine'].exists():
                break
        if m['mine'] is None or not m['mine'].exists():
            self._flashMine(mIndex)
            bs.gameTimer(950, bs.Call(self._makeMine, mIndex))

    def spawnPlayer(self, player):

        # dont allow spawning if this team is done
        if player.getTeam().gameData['finished']:
            return

        pt = self._regions[player.gameData['lastRegion']]._pt
        # dont use the full region so we're less likely to spawn off a cliff
        regionScale = 0.8 
        xRange = ((-0.5, 0.5) if pt[3] == 0
                  else (-regionScale*pt[3], regionScale*pt[3]))
        zRange = ((-0.5, 0.5) if pt[5] == 0
                  else (-regionScale*pt[5], regionScale*pt[5]))
        pt = (pt[0]+random.uniform(*xRange),
              pt[1], pt[2]+random.uniform(*zRange))
        spaz = self.spawnPlayerSpaz(
            player, position=pt, angle=90 if not self._raceStarted else None)

        # prevent controlling of characters before the start of the race
        if not self._raceStarted:
            spaz.disconnectControlsFromPlayer()

        m = bs.newNode('math', owner=spaz.node, attrs={
                       'input1': (0, 1.4, 0), 'operation': 'add'})
        spaz.node.connectAttr('torsoPosition', m, 'input2')
        spaz.distanceTxt = bs.newNode('text',
                                      owner=spaz.node,
                                      attrs={'text': '',
                                             'inWorld': True,
                                             'color': (1, 1, 0.4),
                                             'scale': 0.02,
                                             'hAlign': 'center'})
        m.connectAttr('output', spaz.distanceTxt, 'position')

    def _checkEndGame(self):

        # if there's no teams left racing, finish
        teamsStillIn = len(
            [t for t in self.teams if not t.gameData['finished']])
        if teamsStillIn == 0:
            self.endGame()
            return

        # count the number of teams that have completed the race
        teamsCompleted = len(
            [t for t in self.teams
             if t.gameData['finished'] == True and t.gameData['time'] is not
             None])

        if teamsCompleted > 0:
            # in teams mode its over as soon as any team finishes the race
            if isinstance(self.getSession(), bs.TeamsSession):
                self.endGame()
            else:
                # in ffa we keep the race going while there's still any points
                # to be handed out. find out how many points we have to award
                # and how many teams have finished, and once that matches
                # we're done
                pointsToAward = len(self.getSession()._getFFAPointAwards())
                if teamsCompleted >= pointsToAward-teamsCompleted:
                    self.endGame()
                    return

    def endGame(self):

        # stop updating our time text, and set it to show the exact last
        # finish time if we have one.. (so users dont get upset if their
        # final time differs from what they see onscreen by a tiny bit)
        if self._timer.hasStarted():
            self._timer.stop(endTime=None if self._lastTeamTime is None else (
                self._timer.getStartTime()+self._lastTeamTime))

        results = bs.TeamGameResults()

        for t in self.teams:
            results.setTeamScore(t, t.gameData['time'])
        # we don't announce a winner in ffa mode since its probably been a
        # while since the first place guy crossed the finish line so it seems
        # odd to be announcing that now..
        self.end(results=results, announceWinningTeam=True if isinstance(
            self.getSession(), bs.TeamsSession) else False)

    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self, m)  # augment default
            try:
                player = m.spaz.getPlayer()
                if player is None:
                    bs.printError('FIXME: getPlayer() should no '
                                  'longer ever be returning None')
                else:
                    if not player.exists():
                        raise Exception()
                team = player.getTeam()
            except Exception:
                return
            if not player.gameData['finished']:
                self.respawnPlayer(player, respawnTime=1000)
        else:
            bs.TeamGameActivity.handleMessage(self, m)

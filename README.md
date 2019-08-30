<h1>BombSquad Mods By MythB</h1>

<h2>Hi There!</h2>

These are my mods for the game
<a href="http://www.froemling.net/apps/bombsquad">BombSquad</a> by 
<a href="http://www.froemling.net/about">Eric Froemling</a>

**Check Out My Modded BombSquad Server !** <br />
Download [MythBServerButton.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBServerButton.py)<br />
Add to your bombsquad mod folder in your device.<br />
Ta da ! My server button will apeear in mainmenu, you can easily join my server from there.<br />
[Usage](#Usage)  <br />

<h2>Contents</h2>

[Custom Powerups](#CustomPowerups)  <br />
[Ranking System](#RankingSystem) <br />
[Admin System](#AdminSystem) <br />
[Chat Message Log](#ChatMessageLog)<br />
[Custom Game Modes](https://github.com/user/repo/blob/branch/other_file.md)<br />

<h2>CustomPowerups</h2>

| Image | Name | Info |
| ---------- | -------- |-------- |
|   ![SuperStar](https://github.com/MythB/BombSquad-Mods/blob/master/Media/superStar.png)   |  SuperStar   |Makes you Invincible for a while. really powerfull!|
|   ![Martyrdom](https://github.com/MythB/BombSquad-Mods/blob/master/Media/Martyrdom.png)   |  Martyrdom   |Drops sticky bombs to your location when you were killed!|
|   ![SpeedBoots](https://github.com/MythB/BombSquad-Mods/blob/master/Media/speedBoots.png)   |  SpeedBoots   |Makes you run FASTER ! you'll love it   |
|   ![Suprise](https://github.com/MythB/BombSquad-Mods/blob/master/Media/suprise.png)   |  Suprise   |Looks like Med-Pack be careful it's FAKE !|
|   ![IceCube](https://github.com/MythB/BombSquad-Mods/blob/master/Media/iceCube.png)   |  IceCube   |Makes you FROZEN !   |


<h2>RankingSystem</h2>

In-game player stats example:
(Displaying only  top 15 players)<br />
For calculating **Fighter ratio:** ```Kill/Death``` <br />
For calculating **Scorer ratio:** ```Score/Played``` <br />
Player must play at least ```20``` games to be listed<br />
 
Admin Trophy ![](https://github.com/MythB/BombSquad-Mods/blob/master/Media/admins.png) |
1st Trophy ![](https://github.com/MythB/BombSquad-Mods/blob/master/Media/1st.png) |
Top 3 Trophy ![](https://github.com/MythB/BombSquad-Mods/blob/master/Media/top3.png) |
Top 15 Trophy ![](https://github.com/MythB/BombSquad-Mods/blob/master/Media/top15.png) |<br />
For fighters trophy on  the```left```, admins at the```center```, scorers on the```right``` over the head of players during playing.
![alt text](https://github.com/MythB/BombSquad-Mods/blob/master/Media/inGamePlayer%20StatsAndServerInfo.png)

<h2>ChatMessageLog</h2>

Name - Message - Date logging.<br />
Storing as HTML Table

![alt text](https://github.com/MythB/BombSquad-Mods/blob/master/Media/chatMessagesLog.jpeg)

<h3>AdminSystem</h3>

<h5>List of admin commands</h5>

| Command | Info |
| ---------- | ---------- |
| /list     | Show playing players id |
| /kick     | kick player |
| /remowe      | Remove player from game |
| /ban /unban    | Ban / unban accounts |
| /amnesty     | Wipe banlist |
| /gj | Announce "Good Job!" to player |
| /kill /killall   | Kill players |
| /curse     | Curse players |
| /heal     | Give heal |
| /freeze /freeze all | Freeze players |
| /thaw | Unfreeze players |
| //headless /headlessall | Cut out the heads ! |
| /shield /shieldall     | Give shield |
| /end | Finish the game |
| /camera | Change camera mode |
| /slow | On/off slow-mo mode |
| /maxplayers | Change maxplayers limit |
| /help | List all possible commands |

<h2>Installation</h2>

<h4>Important Notes !</h4>

<table>
  <tr>
    <td>Rank system<br />
    Admin system(include special commands)<br />
    Chat logging
    <td>Works only on server
    <a href="http://www.files.froemling.net/bombsquad/builds/">builds</a>
  </tr>
  <tr>
   <td>Custom game modes<br />
   Custom powerups
   <td>Works on all 
   <a href="http://www.files.froemling.net/bombsquad/builds/">builds</a>
  </tr>
</table>

**Download the following files**<br />

[MythBAdminCommands.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBAdminCommands.py) <br />
[MythBAdminList.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBAdminList.py) <br />
[MythBChatMessages.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBChatMessages.py) <br />
[MythBPowerups.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBPowerups.py) <br />
[MythBServerAdmin.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBServerAdmin.py) <br />
[MythBServerInfo.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBServerInfo.py) <br />
[MythBStats.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBStats.py) <br />

Move downloaded files to your bombsquad scripts folder<br />

**1**.Open MythBServerInfo.py and ```edit``` ```statsfile folder location``` with your own location and ```edit``` ```serverName string``` with your own server name, save it. (*This is for server info and player stats system*)<br />

**2**.Open MythBChatMessages.py and ```edit```  ```chatfile folder location``` with your own location, save it. (*This is for logging chat messages*)<br />

**3**.Open MythBAdminList.py and ```add``` your account ID to ```AdminList```, save it. (*This makes you admin!*)<br />

**4**.Go to bombsquad scripts folder and ```owerwrite``` the following lines with bsUI.py "_filterChatMessage()"<br />

```python
def _filterChatMessage(msg, clientID):
    if not msg or not msg.strip():
        return None
    else:
        import MythBChatMessages
        MythBChatMessages.collectedMsg(msg, clientID)
        if '/' in msg[0]:
            import MythBAdminCommands
            MythBAdminCommands.cmd(msg, clientID)
            return None
        else:
            return (msg)
```

**5**.Go to bombsquad scripts folder and ```add``` the following 2 lines to bsGame.py "ScoreScreenActivity.onBegin():"
```python
   import MythBStats
   MythBStats.update(self.scoreSet)
```

**6**.Go to bombsquad scripts folder and open bsTeamGame.py ```edit``` the following 2 lines(*Optional*)
``` python
    gDefaultTeamColors = ((0.0, 1.0, 0.0), (1.0, 0.0, 0.0))
    gDefaultTeamNames = ("TEAM 1", "TEAM 2")
```
**7**.For displaying player stats in game, you need to add the ```nameless``` game to your playlist.<br /> To doing this you must download and move ```MythBServerInfo.py``` and ```MythBAdminList.py``` to your bombsquad mod folder in your device.<br />
If you did it right, you should see ```@Player Stats By MythB``` in your playlist.

Thats all !
<h2>Usage</h2>

<h6>Fast Server Button</h6>

Download [MythBServerButton.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBServerButton.py)<br />
Add to your bombsquad mod folder in your device<br />
Ta da ! My server button will apeear in mainmenu, you can easily join my server from there.<br />
![](https://github.com/MythB/BombSquad-Mods/blob/master/Media/serverButton.png)<br />
this script automatically update my server-ip online, so i can change my server config on the fly !
![](https://github.com/MythB/BombSquad-Mods/blob/master/Media/serverButtonWindow.png)

<h6>Fast Admin Commands Shortcut</h6>

Download [MythBAdminShortcut.py](https://github.com/MythB/BombSquad-Mods/blob/master/Utils/MythBAdminShortcut.py)<br />
Add to your bombsquad mod folder in your device<br />
Now you can use commands with clicking on player name at the chat window.
![](https://github.com/MythB/BombSquad-Mods/blob/master/Media/commandShortcuts.png)<br />

<h6>For Custom Games</h6>

You can download custom game modes from [here](https://github.com/MythB/BombSquad-Mods/tree/master/Games)

<h2>License</h2>

[MIT License](https://github.com/MythB/BombSquad-Mods/blob/master/LICENSE)

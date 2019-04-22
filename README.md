# Replay Parser

A replay parser for Necrodancer: AMPLIFIED, which will store all replays into a database for viewing later.

## Building Config File

Copy the `config_template.ini` as `config.ini`. Update any of the defaults if your replay folder doesn't exist there. If you aren't sure, remove the `REPLAY_FOLDER` value, so it reads as `REPLAY_FOLDER=`. The script will ask you to find the folder and then save it to the config file.

## Replay File Information
For ease of viewing, created a new line for each "\n" present in the replay data. Example is a run that ended in 1-3 on Bard
```
94 <- Replay version
-7 <- Mode type (referenced as "t_replay->startingLevel" in code)
1 <- Starting zone
0 <- Starting gold
0 <- Has broadsword
57219 <- Run time in milliseconds
3 <- Total songs played
v Start of first floor information
1492725043 <- First floor seed
1 <- Number of players
480 <- Camera width in pixels assumedly
270 <- Camera height in pixels assumedly
47 <- Keys pressed
9|46|2:2,4:1,6:1,8:1,10:2,12:1,14:1,16:1,18:1,20:1,22:2,24:2,26:2,28:2,30:2,32:2,34:2,36:2,38:2,40:2,42:2,44:1,46:1,48:2,50:2,52:2,54:2,56:2,58:2,60:2,62:2,64:2,66:2,68:1,70:1,72:1,74:2,76:2,78:1,80:2,82:2,84:3,86:2,88:2,90:1,92:1, <- Successful character moves, first # is character, 2nd is # of successful moves, rest is the moves and the beat they occured on
2|11,15, <- Unsuccessful character moves (missed beats etc), first # is unsuccessful moves, followed by the beats they occured on
25 <- No idea
1,0,3,1,3,2,2,0,1,1,0,0,2,1,2,0,0,0,1,0,0,1,1,0,0, <- No idea, probably bat RNG
0 <- No idea

v Start of second floor information
1976763447
1
480
270
51
9|50|2:2,4:2,6:3,8:3,10:2,12:2,14:2,16:2,18:1,20:1,22:2,24:3,26:3,28:2,30:1,32:1,34:0,36:3,38:3,40:2,42:2,44:2,46:3,48:3,50:3,52:3,54:3,56:3,58:3,60:3,62:3,64:1,66:1,68:0,70:1,72:3,74:2,76:3,78:2,80:3,82:3,84:3,86:3,88:3,90:3,92:3,94:2,96:3,98:0,100:3,
0|
11
0,0,1,1,2,1,1,0,0,1,1,
0

v Start of third floor information
224999924
1
480
270
33
9|33|2:2,4:2,6:3,8:2,10:2,12:2,14:2,16:3,18:3,20:3,22:1,24:0,26:1,28:0,30:0,32:1,34:1,36:1,38:1,40:1,42:1,44:1,46:1,48:2,50:1,52:2,54:2,56:0,58:0,60:2,62:9,64:9,66:9,
0|
46
0,2,3,0,0,1,2,3,0,2,0,1,3,1,0,0,0,1,0,2,1,0,3,3,3,3,3,1,3,3,0,0,2,2,0,1,1,1,0,3,0,3,0,2,0,0,
0



```
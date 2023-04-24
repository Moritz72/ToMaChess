# ToMaChess  
*ToMaChess* is a gui application to manage chess tournaments written in Python.  
  
## Tournaments  
There are currently four tournament modes available; *Swiss*, *Round Robin*, *Knockout* and *Custom*.  
  
*Swiss* uses the Dutch System from [bbpPairings](https://github.com/BieremaBoyzProgramming/bbpPairings) to pair the rounds.  
The user can specify the parameters *Rounds*, *Point System* and four *Tiebreak* parameters.  
  
*Round Robin* pairs the rounds by the Circle method (currently with counter-clockwise rotation).   
The user can specify the parameters *Cycles* (single RR, double RR, etc.), *Choose Seating* (if enabled the seating of the first round is done manually), *Point System* and four *Tiebreak* parameters.  
  
*Knockout (Single-elimination)* pairs the first round by dividing the particpants into an upper and a lower bracket by rating and then pairs first player in upper against first lower and so on.  
In succesive rounds the winners of the previous round are again divided into an upper and a lower bracket based on the bracket number they played in in the previous round and paired the same way.  
The user can specify the parameters *Games per Match* (only even values allowed) and an *Armageddon* parameter.  
If there is a tie after the number of games specified, pairs of tiebreak games will be played until either the tie is resolved or the of tiebreak pairs specified in the Armageddon parameter is reached.  
  
*Custom* does not pair at all, instead the user can manually pair all games.  
The user can specify the parameter *Games per Round*, *Rounds*, *Point System* and four *Tiebreak* parameters.  
  
### Tiebreak Criteria  
The possible tiebreak criteria are  
- *Buchholz* (with additional parameters Cut (bottom), Cut (top) and Virtual opponents)  
- *Buchholz Sum* (with additional parameters Cut (bottom), Cut (top) and Virtual opponents)  
- *Sonneborn-Berger* (with additional parameters Cut (bottom), Cut (top) and Virtual opponents)  
- *Games as black*  
- *Wins as black*  
- *Wins* (with additional parameter Include Forfeits)  
- *Average Rating* (with additional parameters Cut (bottom), Cut (top))  
- *Cumulative Points* (with additional parameters Cut (bottom), Cut (top))  
- *Direct Encounter*  
  
### Armageddon  
For the *Armageddon* parameter the user can specifiy additionaly parameters *with Armageddon*, *After Tiebreak Pair* and *Color Determination* (In order, Random or Choice).  
  
## Multi Stage Tournaments  
One can also combine multiple tournaments to a multi stage tournament.  
A multi stage tournament consists of a first stage with a number of tournaments where the participants are predetermined and an arbitrary number of further stages where the participants of the stage tournaments are the participants that got a certain placement a certain tournament of the previous stage.  

For example one could have *Round Robin* tournaments *Group A* up to *Group H* with four players each in the first stage and then in the second stage a *Knockout* tournament *Finals* with the participants who placed first or second in their respective group.  
The seating for all stages except the first is done manually by the user independent of the usual seating of the tournament mode.  
  
## Teams  
One can create teams, add players to them, remove players from them and change the team order, but I have yet to implement team tournaments.  
  
## Settings  
Currently only font size and the path for bbpPairings.  

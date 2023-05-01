# ToMaChess  
*ToMaChess* is a gui application to manage chess tournaments written in Python.  
Requires PyQt5.
  
## Tournaments  
There are currently four tournament modes available; *Swiss*, *Round Robin*, *Knockout* and *Custom*.  
  
*Swiss* uses the Dutch System from [bbpPairings](https://github.com/BieremaBoyzProgramming/bbpPairings) to pair the rounds.  
The user can specify the parameters *Rounds*, *Point System* and four *Tiebreak* parameters.  
  
*Round Robin* pairs the rounds by the Circle method (currently with counter-clockwise rotation).   
The user can specify the parameters *Cycles* (single RR, double RR, etc.), *Choose Seating* (if enabled the seating of the first round is done manually), *Point System* and four *Tiebreak* parameters.  
  
*Knockout (Single-elimination)* pairs the first round by dividing the particpants into an upper and a lower bracket by rating and then pairs first player in upper against first lower and so on.  
In succesive rounds the winners of the previous round are again divided into an upper and a lower bracket based on the bracket number they played in in the previous round and paired the same way.  
The user can specify the parameters *Games per Match*, *Games per Tiebreak* and an *Armageddon* parameter.  
If there is a tie after the number of games specified, the specified number of tiebreak games will be played until either the tie is resolved or the number of tiebreaks specified in the Armageddon parameter is reached.  
  
*Custom* does not pair at all, instead the user can manually pair all games.  
The user can specify the parameter *Games per Round*, *Rounds*, *Point System* and four *Tiebreak* parameters.  
  
### Tiebreak Criteria  
The possible tiebreak criteria are  
- *Buchholz* (with additional parameters *Cut (bottom)*, *Cut (top)* and *Virtual Opponents*)  
- *Buchholz Sum* (with additional parameters *Cut (bottom)*, *Cut (top)* and *Virtual Opponents*)  
- *Sonneborn-Berger* (with additional parameters *Cut (bottom)*, *Cut (top)* and *Virtual Opponents*)  
- *Games as black*  
- *Wins as black*  
- *Wins* (with additional parameter *Include Forfeits*)  
- *Average Rating* (with additional parameters *Cut (bottom)*, *Cut (top)*)  
- *Cumulative Score* (with additional parameters *Cut (bottom)*, *Cut (top)*)  
- *Direct Encounter*  
  
### Armageddon  
For the *Armageddon* parameter the user can specifiy additionaly parameters *With Armageddon*, *After Tiebreak* and *Color Determination* (In Order, Random or Choice).  
  
## Multi Stage Tournaments  
One can also combine multiple tournaments to a multi stage tournament.  
A multi stage tournament consists of a first stage with a number of tournaments where the participants are predetermined.  
Furthermore, it has an arbitrary number of further stages where the participants of the stage tournaments are the participants that got a certain placement in  a certain tournament of the previous stage.  
  
For example one could have *Round Robin* tournaments *Group A* up to *Group H* with four players each in the first stage and then in the second stage a *Knockout* tournament *Finals* with the participants who placed first or second in their respective group.  
If the option *Draw Lots in Case of Tie* is disabled, it is also possible to create a regular tournament with play-offs in case of a tie for first place by creating a Multi Stage tournament with only the desired regular tournament as the first stage and adding a *Knockout* tournament as a second stage with only the first place as a participant.  
  
## Teams  
Teams are an ordered collection of players.
You can add players to a team, remove players from a team an change the lineup.  
  
### Team Tournaments  
Team tournaments work like regular tournaments, except for some restrictions and changes e.g. for tiebreaks or Armageddon.  
There is an additional parameter *Boards* which specifies on how many boards the matches are played and there are two tiebreak criteria exclusive to team tournaments; *Board Points* and *Berliner Wertung*.  
  
## Settings  
Currently only font size and the path for bbpPairings.  

# 📊 Chess Craziness

A function that takes a PGN string or a game parsed by the `chess` library, and provides an estimated score on how "crazy" the Chess game is. Uses heuristics like sacrificed pieces, promotions, long strings of consecutive king moves, castling checkmate etc. The functions are in craziness.py so you can import from this file to use them.

I've also attached the log files from the searches of Caissabase & the TCEC archive. For some reason there were a lot of games in the human database that seem to have been constructed from randomly generated moves, so you'll have to manually sift through these to find real games. The TCEC one did not have this issue, and is FULL of disgusting games that I haven't had the time to check out. You're all free to look through it yourself and find ones you like!

I will warn you that the code I've written for searching through databases kind of sucks :)

From the YouTube video: [The Craziest Games in Chess](https://www.youtube.com/watch?v=FaOJNknjako)
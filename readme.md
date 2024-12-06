# Chess Craziness

A function that takes a PGN string or a game parsed by the `chess` library, and provides an estimated score on how "crazy" the Chess game is. Uses heuristics like sacrificed pieces, promotions, long strings of consecutive king moves, castling checkmate etc. The functions are in craziness.py so you can import from this file to use them.

I will warn you that the code I've written for searching through databases was pretty much duct taped together to get it to work for the video :)

From the YouTube video: hold on bruh
# Note on the files of the project for each folder:
FeedForward:
- classification.py: train the feedforward neural net to predict match result. Example of save/load trained model to/from disk
- regression.py: train the feedforward neural net to predict probability of winning the match

CNN:
- project2.py: implement the convolutional neural network that predicts hand outcome
- TestModel.py: test a trained model

Gin_Rummy_Python: port Gin Rummy java code into Python
- GinRummyTournamentAI.py: version of GinRummyTournament that use the trained neural network
- GinRummyTournament.py: original version that use 2 heurestic players

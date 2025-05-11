This project involved modifying a Risk-inspired strategy game to support AI players and introduce random game events. The main goal was to make the game more dynamic and intelligent. Random events were added to affect territories and player advantages during gameplay. An AI player was implemented using alpha-beta pruning with a utility function based on the number of territories gained or lost and the loss given to the defender. This helped the AI make better decisions by looking a few moves ahead. The game can also be extended for training AI through reinforcement learning.

Configurable Settings:

- Number of Human Players: Can be adjusted to allow solo or multiplayer sessions.
- Number of AI Players: Choose how many AI opponents participate in a game.
- Random Events: Toggle events that affect the game after every turn.

The project can be start by running these two commands in the root directory, provided that pygame is available

- pip install pygame

- python .\project.py

Or simply enable the environment if you don't want to install the pygame library globally

- .\gameEnv\Scripts\activate

- pip install -r requirements.txt

- python .\project.py

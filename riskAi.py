import copy
from typing import Optional, Tuple, List
from project import RiskGame, Territory, Player, AIPlayer

class RiskAI:
    def __init__(self, depth: int = 3):
        self.max_depth = depth

    def heuristic(self, state: RiskGame, root_owner: Player) -> int:
        """
        Heuristic: net change in number of territories for root_owner
        compared to initial count when search began.
        """
        # Count territories at current state
        current_count = sum(1 for t in state.territories.values() if t.owner == root_owner)
        # Use stored initial count on the AI instance
        return current_count - self.initial_count

    def generate_attack_actions(self, state: RiskGame, player: Player) -> List[Tuple[Territory, Territory]]:
        """
        Generate all valid (src, dest) attack moves for `player`.
        """
        actions = []
        for src in state.territories.values():
            if src.owner == player and src.troops > 1:
                for conn_name in src.connections:
                    dest = state.territories[conn_name]
                    if dest.owner != player:
                        actions.append((src.name, dest.name))
        return actions

    def apply_attack(self, state: RiskGame, action: Tuple[str, str]) -> bool:
        """
        Apply one attack action on state's game.
        Returns True if attack occurred, False if invalid.
        """
        src_name, dst_name = action
        try:
            state.attack(state.territories[src_name], state.territories[dst_name])
            return True
        except ValueError:
            return False

    def alpha_beta(self,
                   state: RiskGame,
                   depth: int,
                   alpha: int,
                   beta: int,
                   maximizing: bool,
                   root_owner: Player) -> Tuple[int, Optional[Tuple[str, str]]]:
        """
        Returns (value, best_action) at this node.
        """
        if depth == 0:
            return self.heuristic(state, root_owner), None

        current_player = state.current_player if maximizing else self.get_opponent(state, root_owner)
        actions = self.generate_attack_actions(state, current_player)
        if not actions:
            # No possible attacks: evaluate state
            return self.heuristic(state, root_owner), None

        best_action = None
        if maximizing:
            value = float('-inf')
            for action in actions:
                new_state = copy.deepcopy(state)
                new_state.current_player = current_player
                self.apply_attack(new_state, action)
                new_state.end_phase()  # proceed game phases if needed
                v, _ = self.alpha_beta(new_state, depth - 1, alpha, beta, False, root_owner)
                if v > value:
                    value, best_action = v, action
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # beta cutoff
            return value, best_action
        else:
            value = float('inf')
            for action in actions:
                new_state = copy.deepcopy(state)
                new_state.current_player = current_player
                self.apply_attack(new_state, action)
                new_state.end_phase()
                v, _ = self.alpha_beta(new_state, depth - 1, alpha, beta, True, root_owner)
                if v < value:
                    value, best_action = v, action
                beta = min(beta, value)
                if beta <= alpha:
                    break  # alpha cutoff
            return value, best_action

    def get_opponent(self, state: RiskGame, player: Player) -> Player:
        # Simplest: pick next in players list
        idx = state.players.index(player)
        return state.players[(idx + 1) % len(state.players)]

    def choose_attack(self, game: RiskGame) -> Optional[Tuple[str, str]]:
        # Initialize root metrics
        self.initial_count = sum(1 for t in game.territories.values() if t.owner == game.current_player)
        value, action = self.alpha_beta(game, self.max_depth, float('-inf'), float('inf'), True, game.current_player)
        return action

# --- Reinforcement Learning Simulation Sketch ---
# You can simulate self-play episodes by looping:
# 
# ai = RiskAI(depth=3)
# for episode in range(NUM_EPISODES):
#     game = RiskGame(players=[ai, ai.clone(), ...])
#     state = game.initial_state()
#     done = False
#     while not done:
#         # For AI-controlled players, choose action via ai.choose_attack
#         action = ai.choose_attack(game)
#         if action:
#             game.attack(game.territories[action[0]], game.territories[action[1]])
#         else:
#             game.advance_phase()
#         # At end of turn, compute reward based on territory count delta
#         if game.is_over():
#             done = True
#         # Use reward to update a value function or policy via RL algorithm (Q-learning, policy gradients, etc.)
# 
# This sketch shows how you could collect (state, action, reward) tuples and train a model
# to approximate the minimax values or a policy.

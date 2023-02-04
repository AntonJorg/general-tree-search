import random
from math import exp, ceil

from src.games import GameState, ConnectFourState, NimState, Twenty48State

class Evaluate:
    """
    Defines methods for implementing TreeSearchAgent.evaluate.

    These methods should:
        - Take a GameState
        - Return an estimate of the utility of the state, as a float (or a list of floats)
        - Not have any side effects
        - Not have to be deterministic
    """
    
    def evaluate_utility(self, state):
        if state.is_terminal:
            return state.utility
        else:
            return None

    def simulate(self, state):
        while not state.is_terminal:
            action = random.choice(state.applicable_actions)
            state = state.result(action)
        return state.utility

    def simulate_many(self, state):        
        values = (self.simulate(state) for _ in range(self.num_simulations))
        return sum(values) / self.num_simulations

    def simulate_stochastic_environment(self, state):
        while not state.is_terminal:
            if hasattr(state, "cumulative_distribution"):
                action = random.choices(state.applicable_actions, 
                    cum_weights=state.cumulative_distribution, 
                    k=1)[0]
            else:
                action = random.choice(state.applicable_actions)
            state = state.result(action)
        return state.utility

    def static_evaluation(self, state):
        match state:
            case ConnectFourState():
                return self._static_eval_connectfour(state)
            case NimState():
                return self._static_eval_nim(state)
            case Twenty48State():
                return self._static_eval_2048(state)
            case _:
                raise ValueError(f"Unknown state type: {type(state)}")

    def _static_eval_connectfour(self, state):
        if state.is_terminal:
            return state.utility

        if state.moves % 2:
            other_pieces = state.player_mask
            current_pieces = state.player_mask ^ state.piece_mask
        else:
            current_pieces = state.player_mask
            other_pieces = state.player_mask ^ state.piece_mask


        shifts = [state.height + 1, 1, state.height, state.height + 2]

        # count 2 connected
        current_two = 0
        other_two = 0
        for shift in shifts:
            current_two += (current_pieces & current_pieces >> shift).bit_count()
            other_two += (other_pieces & other_pieces >> shift).bit_count()
        
        # count three connected
        current_three = 0
        other_three = 0
        for shift in shifts:
            m = current_pieces & current_pieces >> shift
            current_three += (m & m >> shift).bit_count()
            m = other_pieces & other_pieces >> shift
            other_three += (m & m >> shift).bit_count()

        col_mask = 2**(state.height) - 1
        weights = list(range(ceil(state.width / 2))) + list(reversed(range(state.width // 2)))
        weights = (w + 1 for w in weights)

        current_position = 0
        other_position = 0
        for i, weight in enumerate(weights):
            current_position += (current_pieces & col_mask << i * (state.height + 1)).bit_count() * weight
            other_position += (other_pieces & col_mask << i * (state.height + 1)).bit_count() * weight

        score = (current_position - other_position) * .01 + (current_two - other_two) * .1 + current_three - other_three    

        return 1 / (1 + exp(-score))

    def _static_eval_nim(self, state):
        if state.is_terminal:
            return state.utility

        result = 0
        for val in state.array:
            result ^= val

        if state.moves % 2:
            return int(not bool(result))
            
        return int(bool(result))

    def _static_eval_2048(self, state):
        return state.utility
        
    def evaluate_and_simulate(self, state):
        return self.static_evaluation(state), self.simulate(state)

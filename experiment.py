import numpy as np
import random
from constants import *

class Experiment:
    def __init__(self, participant_id, phase_order=None):
        self.participant_id = participant_id
        self.seeds = {}  # Initialize before any method uses it
        self.initial_probs = {}  # Initialize before any method uses it
        self.phase_order = phase_order or self.randomize_phases()
        self.reset_for_phase(self.phase_order[0])
        self.cumulative_earnings = 0
        self.round = 1
        self.data = []

    def randomize_phases(self):
        phases = PHASES.copy()
        random.seed(self.participant_id)
        random.shuffle(phases)
        self.seeds['phase_order'] = self.participant_id
        return phases

    def reset_for_phase(self, phase):
        phase_seed = self.participant_id + phase
        np.random.seed(phase_seed)
        random.seed(phase_seed)
        self.seeds[f'phase_{phase}'] = phase_seed
        self.phase = phase
        self.round = 1
        self.cumulative_earnings = 0
        if phase == 1:
            self.p_safe = SAFE_PROB_INIT
            self.p_uncertain = float(np.random.uniform(UNCERTAIN_PROB_MIN, UNCERTAIN_PROB_MAX))
        elif phase == 2:
            self.p_safe = SAFE_PROB_INIT
            self.p_uncertain = float(np.random.uniform(0.3, 0.7))
        elif phase == 3:
            self.p_safe = float(np.random.uniform(0.2, 0.8))
            self.p_uncertain = float(np.random.uniform(0.3, 0.7))
        self.initial_probs[phase] = {
            'p_safe': self.p_safe,
            'p_uncertain': self.p_uncertain
        }

    def adjust_probabilities(self, box_chosen):
        if box_chosen == 'A':
            self.p_safe = max(PROB_LIMIT_MIN, self.p_safe - PROB_ADJUST)
            self.p_uncertain = min(PROB_LIMIT_MAX, self.p_uncertain + PROB_ADJUST)
        else:
            self.p_safe = min(PROB_LIMIT_MAX, self.p_safe + PROB_ADJUST)
            self.p_uncertain = max(PROB_LIMIT_MIN, self.p_uncertain - PROB_ADJUST)

    def draw_ball(self, box_chosen):
        special = None
        # Log the random seed for this round (for full reproducibility)
        round_seed = self.participant_id + self.phase * 1000 + self.round
        np.random.seed(round_seed)
        random.seed(round_seed)
        self.seeds[f'phase_{self.phase}_round_{self.round}'] = round_seed
        if self.phase == 1:
            prob = self.p_safe if box_chosen == 'A' else self.p_uncertain
            result = np.random.choice(['red', 'black'], p=[prob, 1 - prob])
            if box_chosen == 'A':
                reward = REWARD_RED if result == 'red' else REWARD_BLACK
            else:
                reward = AMBIGUITY_REWARD if result == 'red' else AMBIGUITY_LOSS
        elif self.phase == 2:
            if box_chosen == 'A':
                prob = self.p_safe
                result = np.random.choice(['red', 'black'], p=[prob, 1 - prob])
                reward = REWARD_RED if result == 'red' else REWARD_BLACK
            else:
                prob = self.p_uncertain
                if random.random() < RUMSFELD_SPECIAL_PROB_PHASE3:
                    special = np.random.choice(['gold', 'silver'])
                    result = special
                    reward = REWARD_GOLD if special == 'gold' else REWARD_SILVER
                else:
                    result = np.random.choice(['red', 'black'], p=[prob, 1 - prob])
                    reward = REWARD_RED if result == 'red' else REWARD_BLACK
        elif self.phase == 3:
            if box_chosen == 'A':
                prob = self.p_safe
                result = np.random.choice(['red', 'black'], p=[prob, 1 - prob])
                reward = AMBIGUITY_REWARD if result == 'red' else AMBIGUITY_LOSS
            else:
                prob = self.p_uncertain
                if random.random() < RUMSFELD_SPECIAL_PROB_PHASE3:
                    special = np.random.choice(['gold', 'silver'])
                    result = special
                    reward = REWARD_GOLD if special == 'gold' else REWARD_SILVER
                else:
                    result = np.random.choice(['red', 'black'], p=[prob, 1 - prob])
                    reward = REWARD_RED if result == 'red' else REWARD_BLACK
        return result, reward, special

    def get_initial_probs(self):
        return self.initial_probs

    def get_seeds(self):
        return self.seeds

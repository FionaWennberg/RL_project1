# This file may not be shared/redistributed without permission. Please read copyright notice in the git repo. If this file contains other copyright notices disregard this text.
from collections import defaultdict
from irlc import train
from irlc.ex02.dp_model import DPModel
from irlc.ex02.dp import DP_stochastic
from irlc.ex02.dp_agent import DynamicalProgrammingAgent
from irlc.pacman.pacman_environment import PacmanEnvironment
from irlc.pacman.gamestate import GameState

east = """ 
%%%%%%%%
% P   .%
%%%%%%%% """ 

east2 = """
%%%%%%%%
%    P.%
%%%%%%%% """

SS2tiny = """
%%%%%%
%.P  %
% GG.%
%%%%%%
"""

SS0tiny = """
%%%%%%
%.P  %
%   .%
%%%%%%
"""

SS1tiny = """
%%%%%%
%.P  %
%  G.%
%%%%%%
"""

datadiscs = """
%%%%%%%
%    .%
%.P%% %
%.   .%
%%%%%%%
"""

# TODO: 30 lines missing.
class PacmanDP(DPModel):
    def __init__(self, map_layout: str, N: int):
        super().__init__(N)
        env = PacmanEnvironment(layout_str=map_layout, render_mode=None)
        self._x0, _ = env.reset()
        self._S = get_future_states(self._x0, N)  

    def x0(self):
        return self._x0

    def S(self, k: int):
        return self._S[k]

    def A(self, x, k: int):
        return x.A()

    def gN(self, x):
        return 0
    
    def g(self, x, u, w, k: int):
        return -1 if w.is_won() else 0
    
    def f(self, x, u, w, k: int):
        return w

def p_next(x : GameState, u: str): 
    """ Given the agent is in GameState x and takes action u, the game will transition to a new state xp.
    The state xp will be random when there are ghosts. This function should return a dictionary of the form

    {..., xp: p, ...}

    of all possible next states xp and their probability -- you need to compute this probability.

    Hints:
        * In the above, xp should be a GameState, and p will be a float. These are generated using the functions in the GameState x.
        * Start simple (zero ghosts). Then make it work with one ghosts, and then finally with any number of ghosts.
        * Remember the ghosts move at random. I.e. if a ghost has 3 available actions, it will choose one with probability 1/3
        * The slightly tricky part is that when there are multiple ghosts, different actions by the individual ghosts may lead to the same final state
        * Check the probabilities sum to 1. This will be your main way of debugging your code and catching issues relating to the previous point.
    """
    p = defaultdict(float)
    xp = x.f(u)
    if xp.is_won() or xp.is_lost():
        p[xp] = 1.0
    else:
        ghost_actions = xp.A()
        pg = 1.0 / len(ghost_actions)
        for action in ghost_actions:
            xp_next = xp.f(action)
            p[xp_next] += pg 
    return dict(p)  


def go_east(map): 
    """ Given a map-string map (see examples in the top of this file) that can be solved by only going east, this will return
    a list of states Pacman will traverse. The list it returns should therefore be of the form:

    [s0, s1, s2, ..., sn]

    where each sk is a GameState object, the first element s0 is the start-configuration (corresponding to that in the Map),
    and the last configuration sn is a won GameState obtained by going east.

    Note this function should work independently of the number of required east-actions.

    Hints:
        * Use the GymPacmanEnvironment class. The report description will contain information about how to set it up, as will pacman_demo.py
        * Use this environment to get the first GameState, then use the recommended functions to go east
    """
    env = PacmanEnvironment(layout_str=map, render_mode='human')
    x, info = env.reset()
    states = [x]

    while not x.is_won():
        action = x.A()[0]  # This makes it take the first legal action which happens to be east in the maps we will test on. You can check this by printing x.A() and str(x) to see the map.
        x, reward, done, truncated, info = env.step(action)
        states.append(x)

    return states

def get_future_states(x, N): 
    state_spaces = [[x]]
    for k in range(N):
        sk = state_spaces[k]
        sk_next = []
        for s in sk:
            for u in s.A():
                p = p_next(s, u)   # returns dict {xp: prob}
                for xp in p.keys():
                    if xp not in sk_next:
                        sk_next.append(xp)
        state_spaces.append(sk_next)
    return state_spaces

def win_probability(map, N=10): 
    """ Assuming you get a reward of -1 on wining (and otherwise zero), the win probability is -J_pi(x_0). """
    # TODO: 5 lines missing.
    raise NotImplementedError("Return the chance of winning the given map within N steps or less.")
    return win_probability

def shortest_path(map, N=10): 
    """ If each move has a cost of 1, the shortest path is the path with the lowest cost.
    The actions should be the list of actions taken.
    The states should be a list of states the agent visit. The first should be the initial state and the last
    should be the won state. """
    model = PacmanDP(map, N)
    J, pi = DP_stochastic(model)

    env = PacmanEnvironment(layout_str=map, render_mode='human')
    x, info = env.reset()

    states = [x]
    actions = []

    for k in range(N):
        if x.is_won():
            break
        u = pi[k][x]
        actions.append(u)
        x, reward, done, truncated, info = env.step(u)  # 5 outputs
        states.append(x)
        if done or truncated:
            break

    return actions, states  


def no_ghosts():
    # Check the pacman_demo.py file for help on the GameState class and how to get started.
    # This function contains examples of calling your functions. However, you should use unitgrade to verify correctness.

    ## Problem 7: Lets try to go East. Run this code to see if the states you return looks sensible.
    states = go_east(east)
    for s in states:
        print(str(s))

    ## Problem 8: try the p_next function for a few empty environments. Does the result look sensible?
    x, _ = PacmanEnvironment(layout_str=east).reset()
    action = x.A()[0]
    print(f"Transitions when taking action {action} in map: 'east'")
    print(x)
    print(p_next(x, action))  # use str(state) to get a nicer representation.

    print(f"Transitions when taking action {action} in map: 'east2'")
    x, _ = PacmanEnvironment(layout_str=east2).reset()
    print(x)
    print(p_next(x, action))

    ## Problem 9
    print(f"Checking states space S_1 for k=1 in SS0tiny:")
    x, _ = PacmanEnvironment(layout_str=SS0tiny).reset()
    states = get_future_states(x, N=10)
    for s in states[1]: # Print all elements in S_1.
        print(s)
    print("States at time k=10, |S_10| =", len(states[10]))

    ## Problem 10
    N = 20  # Planning horizon
    action, states = shortest_path(east, N)
    print("east: Optimal action sequence:", action)

    action, states = shortest_path(datadiscs, N)
    print("datadiscs: Optimal action sequence:", action)

    action, states = shortest_path(SS0tiny, N)
    print("SS0tiny: Optimal action sequence:", action)


def one_ghost():
    # Win probability when planning using a single ghost. Notice this tends to increase with planning depth
    wp = []
    for n in range(10):
        wp.append(win_probability(SS1tiny, N=n))
    print(wp)
    print("One ghost:", win_probability(SS1tiny, N=12))


def two_ghosts():
    # Win probability when planning using two ghosts
    print("Two ghosts:", win_probability(SS2tiny, N=12))

if __name__ == "__main__":
    no_ghosts()
    one_ghost()
    two_ghosts()

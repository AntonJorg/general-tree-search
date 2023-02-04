"""
This module defines classes for inheritance into TreeSearchAgent
solely for organizational purposes.

These classes should not be instantiated under normal use.
"""


from gts.agents.components._select import Select
from gts.agents.components.backpropagate import Backpropagate
from gts.agents.components.control import Control
from gts.agents.components.evaluate import Evaluate
from gts.agents.components.expand import Expand
from gts.agents.components.get_best_move import GetBestMove
from gts.agents.components.trim import Reflect

# collect all imports for easy inheritance
components = (Select, Expand, Evaluate, Backpropagate, Reflect, GetBestMove, Control)

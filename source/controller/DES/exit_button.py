"""
Exit controller
Based on the example from todd
"""
import sys

sys.dont_write_bytecode = True


def accept(event, values, state):
    if event in ("Exit", None):
        state["view"].set_result("Exit")
        return False
    return True

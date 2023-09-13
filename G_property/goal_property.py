import xaip.logic.logic_formula as logic_formula
from xaip.general.property import PlanProperty
from xaip.action_sets.action import ActionSet


class GoalProperty(PlanProperty):

    def __init__(self, name, formula, weaker=[], stronger=[]):
        super().__init__(name, formula, weaker, stronger)


    @staticmethod
    def fromJSON(json, typeObjectMap):
        formula = json['formula']
        weaker = []
        stronger = []
        if 'weaker' in json:
            weaker = json['weaker']
        if 'stronger' in json:
            stronger = json['stronger']
        new_property = GoalProperty(json['name'], formula,weaker, stronger)
        return new_property

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

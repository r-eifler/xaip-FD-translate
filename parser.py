import json

from .G_property.goal_property import GoalProperty
from .AS_property.action_set_property import ActionSetProperty
from .LTL_property.LTL_property import LTLProperty
from .general.special_goals import Goal
from .depper_why_questions import relaxed_task

# typeObjectMap maps from a type to a list of objects which have this type
def parse(json_encoding, typeObjectMap, EXPSET):

    if "plan_properties" in json_encoding:
        for p_json in json_encoding["plan_properties"]:
            if p_json['type'] == 'AS':
                property = ActionSetProperty.fromJSON(p_json, typeObjectMap)
                EXPSET.add_action_set_property(property)
            elif p_json['type'] == 'LTL':
                property = LTLProperty.fromJSON(p_json, typeObjectMap)
                EXPSET.add_ltl_property(property)
            elif p_json['type'] == 'G':
                property = GoalProperty.fromJSON(p_json, typeObjectMap)
                EXPSET.add_goal_property(property)
            else:
                assert False, "Unknown property type: " + p_json['type']
            for set in property.get_action_sets():
                oldName = set.name
                EXPSET.add_action_set(set)
                # print("Replace constant name: " + oldName + " " + set.name)
                property.update_action_set_name(oldName, set.name)

    if "hard_goals" in json_encoding:
        EXPSET.init_hard_goals()
        EXPSET.add_hard_goals(Goal.fromJSON(json_encoding["hard_goals"], EXPSET))

    if "soft_goals" in json_encoding:
        EXPSET.init_soft_goals()
        EXPSET.add_soft_goals(Goal.fromJSON(json_encoding["soft_goals"], EXPSET))

    if "only_use_here_specified_goals" in json_encoding:
        EXPSET.only_use_here_specified_goals = json_encoding["only_use_here_specified_goals"]

    if 'relaxed_tasks' in json_encoding:
        EXPSET.relaxed_tasks = relaxed_task.parse_tasks(json_encoding['relaxed_tasks'])

    if 'not_pruned_facts' in json_encoding:
        EXPSET.not_pruned_facts = json_encoding["not_pruned_facts"]

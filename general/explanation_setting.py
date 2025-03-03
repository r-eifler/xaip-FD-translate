
class ExplanationSetting:

    def __init__(self):
        self.action_sets = {}
        self.action_set_properties = {}
        self.ltl_properties = {}
        self.g_properties = {}

        self.only_use_here_specified_goals = False
        self.hard_goals = None
        self.soft_goals = None

        self.relaxed_tasks = []

        self.not_pruned_facts = []

        self.partial_order = None

    def init_soft_goals(self):
        self.soft_goals = []

    def init_hard_goals(self):
        self.hard_goals = []

    def add_action_set(self, set):
        # assert set.name not in self.action_sets
        set.name = set.name + '_' + str(len(self.action_sets)) # unique name for each action set
        self.action_sets[set.name] = set

    def add_action_set_property(self, prop):
        assert prop.name not in self.action_set_properties and \
               prop.name not in self.ltl_properties and \
               prop.name not in self.g_properties, \
            "Not unique plan property name: " + prop.name
        # prop.name = prop.name + '_' + str(len(self.action_set_properties) + len(self.ltl_properties))  # unique name for each action set
        self.action_set_properties[prop.name] = prop

    def add_ltl_property(self, prop):
        assert prop.name not in self.action_set_properties and \
               prop.name not in self.ltl_properties and \
               prop.name not in self.g_properties, \
            "Not unique plan property name: " + prop.name
        # prop.name = prop.name + '_' + str(
        # len(self.action_set_properties) + len(self.ltl_properties))  # unique name for each action set
        self.ltl_properties[prop.name] = prop

    def add_goal_property(self, prop):
        assert prop.name not in self.action_set_properties and \
               prop.name not in self.ltl_properties and \
               prop.name not in self.g_properties, \
            "Not unique plan property name: " + prop.name
        self.g_properties[prop.name] = prop

    def get_action_sets(self):
        return list(self.action_sets.values())

    def get_action_set_properties(self):
        return list(self.action_set_properties.values())

    def get_ltl_properties(self):
        return list(self.ltl_properties.values())

    def get_goal_properties(self):
        return list(self.g_properties.values())
    
    def get_partial_order_properties(self):
        return list(self.partial_order)

    def get_property(self, name):
        # print("get: " + name)
        # print(self.ltl_properties[name]);
        if name in self.action_set_properties:
            return self.action_set_properties[name]
        elif name in self.ltl_properties:
            return self.ltl_properties[name]
        elif name in self.g_properties:
            return self.g_properties[name]
        return None

    def has_hard_goals(self):
        return self.hard_goals is not None

    def has_soft_goals(self):
        return self.soft_goals is not None
    
    def has_partial_order(self):
        return self.partial_order is not None

    def add_hard_goal(self, goal):
        # print("Hard goals: ")
        # print(self.hard_goals)
        if self.hard_goals is None:
            self.hard_goals = []
        assert self.soft_goals is None or goal not in self.soft_goals
        assert goal not in self.hard_goals, "Already contained: " + str(goal)
        self.hard_goals.append(goal)

    def add_hard_goals(self, goals):
        if self.hard_goals is None:
            self.hard_goals = []
        for g in goals:
            self.add_hard_goal(g)

    def add_soft_goal(self, goal):
        if self.soft_goals is None:
            self.soft_goals = []
        assert self.hard_goals is None or goal not in self.hard_goals
        assert goal not in self.soft_goals, "Already contained: " + str(goal)
        self.soft_goals.append(goal)

    def add_soft_goals(self, goals):
        if self.soft_goals is None:
            self.soft_goals = []
        for g in goals:
            self.add_soft_goal(g)

    def add_relaxed_task(self, task):
        self.relaxed_tasks.append(task)

    def get_relaxed_tasks(self):
        return self.relaxed_tasks
    
    def add_not_pruned_fact(self, fact):
        self.not_pruned_facts.append(fact)

    def get_not_pruned_facts(self):
        return self.not_pruned_facts
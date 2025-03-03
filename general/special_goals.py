from xaip.G_property.goal_property import GoalProperty
from xaip.general.utils import literalVarValue, varValueLiteral

class Goal:

    def __init__(self, var_name, var_id=None, value=None):
        self.var_name = var_name
        self.var_id = var_id
        self.value = value

    def get_sas_fact(self, sas_task, EXPSET):

        if self.var_id is not None and self.value is not None:
            return self.var_id, self.value
        if self.var_name:
            prop = EXPSET.get_property(self.var_name)
            if prop:
                self.var_id = prop.var_id
                self.value = prop.var_sat_goal_value
            else:
                self.var_id, self.value = literalVarValue(sas_task, self.var_name)
            assert self.var_id is not None and self.value is not None, "ERROR: invalid goal: " + self.var_name
            return self.var_id, self.value

    def __eq__(self, other):
        return self.var_name == other.var_name or (self.var_id and other.var_id  and self.var_id == other.var_id)

    def __hash__(self):
        return hash(self.var_name)

    @staticmethod
    def fromJSON(json, EXPSET):
        goals = []
        for goal_name in json:
            new_goal = Goal(goal_name)
            goals.append(new_goal)
        return goals

    def __repr__(self):
        return self.var_name + ": " + str(self.var_id) + "=" + str(self.value)


# adds the hard and soft goals as specified in the explanation setting and
# checks that the overall goals only contains the facts which are either in
# the soft or in the hard goals
def set_goals(sas_task, EXPSET, options):
    print("****************************************************************************")
    # if there are hard goals then they can be necessary for the LTLf compilation
    # so they need to stay hardgoals
    
    soft_goals = []
    
    if (EXPSET.has_hard_goals() and EXPSET.has_soft_goals()) or EXPSET.only_use_here_specified_goals:
        print("hard AND soft goals are specified (goals not specified as hard or soft goals are not considered)")
        print("only_use_here_specified_goals: " + str(EXPSET.only_use_here_specified_goals))
        # add hard goals
        for hg in EXPSET.hard_goals:
            sas_task.addHardGoalFact(hg.get_sas_fact(sas_task, EXPSET))

        # add soft goals
        for sg in EXPSET.soft_goals:
            soft_goals.append(sg)
            sas_task.addSoftGoalFact(sg.get_sas_fact(sas_task, EXPSET))

        # make goals consistent with hard + soft goals
        sas_task.goal.reset_facts([g.get_sas_fact(sas_task, EXPSET) for g in EXPSET.hard_goals + EXPSET.soft_goals])
    
    elif EXPSET.has_hard_goals():
        print("hard goals are specified but not soft goals -> original goal facts and all remaining properties are soft goals")
        
        # add original goals as soft goals
        for gf in sas_task.goal.pairs:
            sas_task.addSoftGoalFact(gf)
            fact = varValueLiteral(sas_task, gf[0], gf[1])
            soft_goals.append(GoalProperty(fact, fact))
        
        # add hard goals
        hard_goal_names = []
        for hg in EXPSET.hard_goals:
            hard_goal_names.append(hg.var_name)
            pair = hg.get_sas_fact(sas_task, EXPSET)
            sas_task.addHardGoalFact(pair)
            sas_task.goal.pairs.append(pair)

        # add properties as soft goal
        for pg in (EXPSET.get_action_set_properties() + EXPSET.get_ltl_properties() + EXPSET.get_goal_properties()):
            if pg.name in hard_goal_names:
                continue
            pair = Goal(pg.name).get_sas_fact(sas_task, EXPSET)
            sas_task.addSoftGoalFact(pair)
            sas_task.goal.pairs.append(pair)
            soft_goals.append(pg)

    else:
        print("No hard and no soft goals -> original goal facts and all properties are soft goals")
        for i, gf in enumerate(sas_task.goal.pairs):
            sas_task.addSoftGoalFact(gf)
            fact = varValueLiteral(sas_task, gf[0], gf[1])
            soft_goals.append(GoalProperty(fact, fact))

        for pg in EXPSET.get_action_set_properties() + EXPSET.get_ltl_properties() + EXPSET.get_goal_properties():
            pair = Goal(pg.name).get_sas_fact(sas_task, EXPSET)
            sas_task.addSoftGoalFact(pair)
            sas_task.goal.pairs.append(pair)
            soft_goals.append(pg)
            
    
    if hasattr(sas_task, "addSoftGoalGraph"):
        # update soft goal graph
        edges = set()
        for sg in soft_goals:
            sg_pair = Goal(sg.name).get_sas_fact(sas_task, EXPSET)
            edges.add((sg_pair, sg_pair))
            for w in sg.weaker:
                edges.add((sg_pair, Goal(w).get_sas_fact(sas_task, EXPSET)))
            for s in sg.stronger:
                edges.add((Goal(s).get_sas_fact(sas_task, EXPSET), sg_pair))

        if EXPSET.has_partial_order():
            print("has partial order")
        
            for goal_names in EXPSET.get_partial_order_properties():

                if isinstance(goal_names, list) and len(goal_names) >= 2:
                    # First element is higher priority, second is lower priority
                    goal_name_higher = goal_names[0]
                    goal_name_lower = goal_names[1]
                    
                    # Create Goal objects for the ordered properties
                    goal_higher = Goal(goal_name_higher)
                    goal_lower = Goal(goal_name_lower)
                    
                    # Get SAS facts for these goals

                    try:
                        fact_higher = goal_higher.get_sas_fact(sas_task, EXPSET)
                        fact_lower = goal_lower.get_sas_fact(sas_task, EXPSET)
                        
                        # Add edge representing the partial order relationship
                        edges.add((fact_higher, fact_lower))
                        print(f"Added partial order edge: {goal_names[0]} > {goal_names[1]}")

                    except Exception as e:
                        print(f"Failed to add partial order edge for {goal_name_higher} > {goal_name_lower}: {e}")
                

        # for testing add edges from i to i + 1 to achieve lex ordering
        # later include odering from json input
        # for i in range(len(soft_goals) - 1):
        #     a = Goal(soft_goals[i].name).get_sas_fact(sas_task, EXPSET)
        #     b = Goal(soft_goals[i+1].name).get_sas_fact(sas_task, EXPSET)
        #     edges.add((a,b))
        #     if i % 2 == 1:
        #         a = Goal(soft_goals[i].name).get_sas_fact(sas_task, EXPSET)
        #         b = Goal(soft_goals[i+1].name).get_sas_fact(sas_task, EXPSET)
        #         edges.add((b,a))


        
        print('------ soft goal graph ----')
        print('num edges: ' + str(len(edges)))
        for e in edges:
            print(e)
        sas_task.addSoftGoalGraph(list(edges))
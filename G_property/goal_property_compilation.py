from xaip.logic import logic_formula
from xaip.general.utils import literalVarValueList
from sas_tasks import *
from xaip.general.utils import literalVarValue


def compile_single_goal_fact(sas_task, property):
    var, value = literalVarValue(sas_task, property.formula.name)
    assert var is not None and value is not None, "ERROR: invalid goal: " + property.name + ' #variables: ' + str(sas_task.variables.value_names)
    property.var_id = var
    property.var_sat_goal_value = value
    
    
def addPropertySatVariables(sas_task, prop):
    # compile property into one (goal) fact 
    #fact that indicates if the property is satisfied at the end of the plan
    prop.var_id = len(sas_task.variables.value_names)
    prop_vars = ["not_sat_" + prop.name, "sat_" + prop.name]

    #print(prop.name + " : " + str(prop.var_id))

    sas_task.variables.value_names.append(prop_vars)
    sas_task.variables.ranges.append(len(prop_vars)) #binary var
    sas_task.variables.axiom_layers.append(-1)

    # update initial state -> at the beginning the property is not satisfied
    sas_task.init.values.append(0)

def addPropertyCheckingActions(sas_task, prop):
    #add the actions checking if the property ist true
    # Assumption: property is in disjunctive normal form

    # print("Clauses: \n Property: " + str(prop))
    #for every clause in DNF we have to create one action
    clauses = prop.getClauses()
    # print(clauses)
    for c in clauses:
        pre_post = []
        # literals form the preconditions
        for l in c:
            facts = literalVarValueList(sas_task, l.constant.name, l.negated)
            assert len(facts) > 0, "Fact " + l + ' does not exist.'
            for fact in facts:
                pre_post.append((fact[0],fact[1],fact[1],[]))

        # as effect the property fact is set to true
        pre_post.append((prop.var_id, -1, 1, []))

        # print(pre_post)
        sas_task.operators.append(SASOperator("(" + prop.name + "_ " + str(c) + ")",[], pre_post, 0))
    
    
def compile(sas_task, property):
    # print("**************************************************************")
    # print(property)
    if isinstance(property.formula, logic_formula.LConstant):
        print('compile_single_goal_fact')
        compile_single_goal_fact(sas_task,property)
        return
    
    addPropertySatVariables(sas_task, property)
    addPropertyCheckingActions(sas_task, property)
        

def compileGoalProperties(sas_task, properties):
    for prop in properties:
        compile(sas_task, prop)

        

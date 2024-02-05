
def find_var_value_id(sas_variables, fact):
    negated = fact.startswith('!')
    pure_fact = fact.replace('! ','')
    for var_id, variable in enumerate(sas_variables):
        for value_id, value in enumerate(variable):
            if (negated and 'NegatedAtom ' + pure_fact == value) or (not negated and 'Atom ' + pure_fact == value):
                return var_id, value_id
    #return None
    #print('Warning: ' + fact + ' not in ' + str(sas_variables))
    assert False, fact + ' not in ' + str(sas_variables)


def parse_tasks(json_def):
    return [RelaxedTask.parse(tj) for tj in json_def]


class ApplicableAction:

    def __init__(self, name, params, param_id, upper_bound, lower_bound) -> None:
        self.name = name
        self.params = params
        self.param_id = param_id
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    @staticmethod
    def parse(json_def):
        return ApplicableAction(json_def["name"], json_def["params"], 
                                json_def["param_id"], json_def["upper_bound"],
                                json_def["lower_bound"])


class RelaxedTask:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.init = []
        self.init_fact_names = []
        self.applicable = []

        self.upper_cover = []
        self.lower_cover = []

    def get_init_fact_names(self):
        # return []
        return [f.replace('! ','') for f in self.init_fact_names]

    def __repr__(self):
        return str(self.id) + ': ' + self.name + '\n ' + str(self.init) + '\n ' + str(self.limits) + '\n ' + str(self.cover)

    def update_init_and_limits(self, sas_task):
        # pass
        var_names = sas_task.variables.value_names
        self.init = [find_var_value_id(var_names,f) for f in self.init_fact_names]

    @staticmethod
    def parse(json_def):
        print(json_def)
        assert ('name' in json_def and 'id' in json_def and 'upper_cover' in json_def and 'lower_cover' in json_def)
        assert ('inits' in json_def or 'applicable' in json_def)

        id = json_def['id']
        name = json_def['name']

        newTask = RelaxedTask(id, name)

        newTask.lower_cover = json_def['lower_cover']
        newTask.upper_cover = json_def['upper_cover']

        if 'inits' in json_def:
            newTask.init_fact_names = json_def['inits']

        if 'applicable' in json_def:
            for jd in json_def["applicable"]:
                newTask.applicable.append(ApplicableAction.parse(jd))

        return newTask





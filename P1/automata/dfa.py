from automata.automaton import State, Transitions, FiniteAutomaton
from automata.utils import is_deterministic
from collections import deque

class DeterministicFiniteAutomaton(FiniteAutomaton):    
    @staticmethod
    def to_deterministic(finiteAutomaton):

    
    # To avoid circular imports
        from automata.automaton_evaluator import FiniteAutomatonEvaluator
        evaluator = FiniteAutomatonEvaluator(finiteAutomaton)
        
        first_set = sorted(evaluator.current_states, key=lambda state: state.name)
        name = "".join(str(state.name) for state in first_set)

        init_state = State(name, any(state.is_final for state in first_set))
        
        tabla = dict()
        list_states = list()

        list_states.append(first_set)
        
        set_states = set()

        set_states.add(init_state)

        while list_states:
            est = list_states.pop(0)
            
            if est == []:
                name_prev = "empty"
            else:
                name_prev = "".join(state.name for state in est)
            prev_state = State(name_prev, any(state.is_final for state in est))
            
            tabla[prev_state] = dict()
            
            symbols_iter = iter(evaluator.automaton.symbols)
            while True:
                try:
                    symbol = next(symbols_iter)
                except StopIteration:
                    break

                evaluator.current_states = set(est)
                evaluator.process_symbol(symbol)

                set_estados = sorted(evaluator.current_states, key=lambda state: state.name)

                if set_estados == []:
                    name = "empty"
                else:
                    name = "".join(state.name for state in set_estados)
                state = State(name, any(state.is_final for state in set_estados))

                tabla[prev_state][symbol] = {state}

                if state not in tabla:
                    list_states.append(set_estados)
                    set_states.add(state)
                evaluator.current_states = set(est)

            
        #---------------------------------------------------------------------
        return FiniteAutomaton(init_state, set_states, evaluator.automaton.symbols, tabla)

    

    @staticmethod
    def to_minimized(dfa):
        
        def create_from_dictionary(d):
            d_res = dict()

            d_iter = iter(d.items())
            while True:
                try:
                    clase, k = next(d_iter)
                except StopIteration:
                    break

                d_res[clase] = create_from_sets(frozenset(k))


            return d_res

        def create_from_sets(s):
            
            is_final = any(state.is_final for state in s)
            nombre = "".join(str(state.name) for state in s)

            st = State(nombre, is_final)
            return st

        from automata.automaton_evaluator import FiniteAutomatonEvaluator
        evaluator = FiniteAutomatonEvaluator(dfa)

        visited = dict()
        for nd in dfa.states:
            visited[nd] = 0

        for state in evaluator.current_states:
            visited[state] = 1

        queue = list(evaluator.current_states)
        while len(queue) != 0:
            new_visited = list()
            for first_state in queue:

                for symbol in dfa.symbols:
                    evaluator.current_states = {first_state}
                    evaluator.process_symbol(symbol)

                    for s_state in evaluator.current_states:
                        if visited[s_state] == 0:
                            visited[s_state] = 1
                            new_visited.append(s_state)

            queue = new_visited

        states = [state for state, marked in visited.items() if marked == 1]

        prev = dict()
        current = dict()

        states_iter = iter(states)
        while True:
            try:
                th_state = next(states_iter)
            except StopIteration:
                break

            if th_state.is_final is False:
                prev[th_state] = 0
                current[th_state] = 0
            else:
                current[th_state] = 1
                prev[th_state] = 1


        flag = False
        while not flag:
            i = 0
            prev = current
            current = dict()
            for state in prev.keys():
                if state not in current.keys():
                    current[state] = i
                    for flag2 in prev.keys():
                        if flag2 not in current.keys():
                            if prev[state] == prev[flag2]:
                                flag3 = True
                                for symbol in dfa.symbols:
                                    evaluator.current_states = {state, flag2}
                                    evaluator.process_symbol(symbol)
                                    reference_state = list(evaluator.current_states)[0]
                                    reference_value = prev[reference_state]
                                    if not all(prev[key] == reference_value for key in evaluator.current_states):
                                        flag3 = False
                                if flag3:
                                    current[flag2] = i
                    i += 1

            if not current:
                return False

            flag = all(current[state] == prev[state] for state in prev.keys())

        same_class = dict()
        states_iter = iter(current.items())
        while True:
            try:
                state, clase = next(states_iter)
            except StopIteration:
                break
            
            if clase not in same_class.keys():
                same_class[clase] = set()
            same_class[clase].add(state)


        final = create_from_dictionary(same_class)

        self = DeterministicFiniteAutomaton(final[0], final.values(), dfa.symbols, dict())

        transitions = list()
        clases_iter = iter(same_class.items())
        while True:
            try:
                clase, estados = next(clases_iter)
            except StopIteration:
                break
            
            symbols_iter = iter(dfa.symbols)
            while True:
                try:
                    symbol = next(symbols_iter)
                except StopIteration:
                    break
                
                evaluator.current_states = frozenset(estados)
                evaluator.process_symbol(symbol)
                transitions.append((final[clase], symbol, final[current[list(evaluator.current_states)[0]]]))


        self.add_transitions(transitions)

        return self

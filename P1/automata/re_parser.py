"""Conversion from regex to automata."""
from automata.automaton import FiniteAutomaton, State, Transitions
from typing import Collection, Set, List

def _re_to_rpn(re_string):
    """
    Convert re to reverse polish notation (RPN).

    Does not check that the input re is syntactically correct.

    Args:
        re_string: Regular expression in infix notation. Type: str

    Returns:
        Regular expression in reverse polish notation. Type: str

    """
    stack = [] # List of strings
    rpn_string = ""
    for x in re_string:
        if x == "+":
            while len(stack) > 0 and stack[-1] != "(":
                rpn_string += stack.pop()
            stack.append(x)
        elif x == ".":
            while len(stack) > 0 and stack[-1] == ".":
                rpn_string += stack.pop()
            stack.append(x)
        elif x == "(":
            stack.append(x)
        elif x == ")":
            while stack[-1] != "(":
                rpn_string += stack.pop()
            stack.pop()
        else:
            rpn_string += x

    while len(stack) > 0:
        rpn_string += stack.pop()

    return rpn_string



class REParser():
    """Class for processing regular expressions in Kleene's syntax."""
    
    def _init_(self) -> None:
        self.state_counter = 0

    def _create_automaton_empty(self):
        q0 = State("q0", False)
        q1 = State("q1", True)
        states = set()
        states.add(q0)
        states.add(q1)
        trans = Transitions()

        aut = FiniteAutomaton(q0, states, None, trans)

        return aut

    def _create_automaton_lambda(self):
        q0 = State("q0", True)
        states = set()
        states.add(q0)
        trans = Transitions()

        return FiniteAutomaton(q0, states, None, trans)

    def _create_automaton_symbol(self, symbol):
        q0 = State("q0", False)
        q1 = State("q1", True)
        states = set()
        states.add(q0)
        states.add(q1)
        trans = Transitions()

        trans.add_transition(q0, symbol, q1)

        return FiniteAutomaton(q0, states, {symbol}, trans)

    def _create_automaton_star(self, automaton):
        states = set()
        new_andold = dict()
        symbols = set()
        transitions_getted = automaton.get_all_transitions()
        cont = 0

        q0 = State("q"+str(self.state_counter), False)
        self.state_counter += 1
        states.add(q0)

        initial = automaton.initial_state

        for i in automaton.states:
            if i.is_final:
                i.is_final = False
                final = State("q"+str(self.state_counter))
                states.add(final)
                new_andold[i] = final
            else:
                new_andold[i] = State("q" + str(self.state_counter))
                states.add(new_andold[i])
                if i.name == initial.name:
                    initial = new_andold[i]

            self.state_counter += 1

        qf = State("q"+str(self.state_counter), True)
        self.state_counter += 1
        states.add(qf)

        trans = Transitions()

        trans.add_transition(q0, None, initial)
        trans.add_transition(q0, None, qf)
        trans.add_transition(final, None, initial)
        trans.add_transition(final, None, qf)

        for each in transitions_getted:
            for i in each:
                cont += 1
                if cont == 1:
                    s1 = new_andold[i]  
                if cont == 2:
                    symbol = i
                    symbols.add(str(i))  
                if cont == 3:
                    s2 = new_andold[i]  
                    trans.add_transition(s1, symbol, s2)
                    cont = 0 

        return FiniteAutomaton(q0, states, symbols, trans)

    def _create_automaton_union(self, automaton1, automaton2):
        states = set()
        symbols = set()
        new_andold = dict()
        finals = list()
        initials = list()

        q0 = State("q"+str(self.state_counter), False)
        self.state_counter += 1
        states.add(q0)

        automatons = [automaton1, automaton2]

        for automaton_n in range(len(automatons)):
            automaton = automatons[automaton_n]
            initial = automaton.initial_state
            new_andold[automaton_n] = dict()

            for i in automaton.states:
                if i.is_final:
                    i.is_final = False
                    final = State("q"+str(self.state_counter))
                    states.add(final)
                    new_andold[automaton_n][i] = final
                    finals.append(final)
                else:
                    new_andold[automaton_n][i] = State("q" + str(self.state_counter))
                    states.add(new_andold[automaton_n][i])

                    if i.name == initial.name:
                        initial = new_andold[automaton_n][i]
                        initials.append(initial)

                self.state_counter += 1

        f0 = State("f"+str(self.state_counter), True)
        self.state_counter += 1
        states.add(f0)

        trans = Transitions()

        trans.add_transition(q0, None, initials[0])
        trans.add_transition(q0,None, initials[1])
        trans.add_transition(finals[0], None, f0)
        trans.add_transition(finals[1], None, f0)

        for automaton_n in range(len(automatons)):
            automaton = automatons[automaton_n]
            transitions_getted = automaton.get_all_transitions()
            cont = 0
            for each in transitions_getted:
                for i in each:
                    cont += 1
                    if cont == 1:
                        s1 = new_andold[automaton_n][i]  
                    if cont == 2:
                        symbol = i
                        symbols.add(str(i))  
                    if cont == 3:
                        s2 = new_andold[automaton_n][i]  
                        trans.add_transition(s1, symbol, s2)
                        cont = 0 

        return FiniteAutomaton(q0, states, symbols, trans)

    def _create_automaton_concat(self, automaton1, automaton2):
        states = set()
        symbols = set()
        new_andold = dict()
        finals = list()
        initials = list()

        automatons = [automaton1, automaton2]

        for automaton_n in range(len(automatons)):
            automaton = automatons[automaton_n]
            initial = automaton.initial_state
            new_andold[automaton_n] = dict()

            for i in automaton.states:
                if i.is_final:
                    i.is_final = (automaton_n == 1)
                    final = State("q"+str(self.state_counter), i.is_final)
                    states.add(final)
                    new_andold[automaton_n][i] = final
                    finals.append(final)
                else:
                    new_andold[automaton_n][i] = State("q" + str(self.state_counter))
                    states.add(new_andold[automaton_n][i])

                    if i.name == initial.name:
                        initial = new_andold[automaton_n][i]
                        initials.append(initial)

                self.state_counter += 1

        trans = Transitions()

        trans.add_transition(finals[0], None, initials[1])

        for automaton_n in range(len(automatons)):
            automaton = automatons[automaton_n]
            transitions_getted = automaton.get_all_transitions()
            cont = 0
            for each in transitions_getted:
                for i in each:
                    cont += 1
                    if cont == 1:
                        s1 = new_andold[automaton_n][i]  
                    if cont == 2:
                        symbol = i
                        symbols.add(str(i))  
                    if cont == 3:
                        s2 = new_andold[automaton_n][i]  
                        trans.add_transition(s1, symbol, s2)
                        cont = 0 

        return FiniteAutomaton(initials[0], states, symbols, trans)


    def create_automaton(
        self,
        re_string,
    ):
        """
        Create an automaton from a regex.

        Args:
            re_string: String with the regular expression in Kleene notation. Type: str

        Returns:
            Automaton equivalent to the regex. Type: FiniteAutomaton

        """
        if not re_string:
            return self._create_automaton_empty()
        
        rpn_string = _re_to_rpn(re_string)

        stack = [] # list of FiniteAutomatons

        self.state_counter = 0
        for x in rpn_string:
            if x == "*":
                aut = stack.pop()
                stack.append(self._create_automaton_star(aut))
            elif x == "+":
                aut2 = stack.pop()
                aut1 = stack.pop()
                stack.append(self._create_automaton_union(aut1, aut2))
            elif x == ".":
                aut2 = stack.pop()
                aut1 = stack.pop()
                stack.append(self._create_automaton_concat(aut1, aut2))
            elif x == "λ":
                stack.append(self._create_automaton_lambda())
            else:
                stack.append(self._create_automaton_symbol(x))

        return stack.pop()
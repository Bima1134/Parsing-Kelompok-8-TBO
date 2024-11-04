import argparse
import string
from collections import defaultdict
from nltk.tree import Tree

class Rule(object):
    def __init__(self, lhs, rhs):
        self.lhs, self.rhs = lhs, rhs

    def __contains__(self, sym):
        return sym in self.rhs

    def __eq__(self, other):
        return isinstance(other, Rule) and self.lhs == other.lhs and self.rhs == other.rhs

    def __getitem__(self, i):
        return self.rhs[i]

    def __len__(self):
        return len(self.rhs)

    def __str__(self):
        return self.lhs + ' -> ' + ' '.join(self.rhs)

class Grammar(object):
    def __init__(self):
        self.rules = defaultdict(list)

    def add(self, lhs, rhs):
        self.rules[lhs].append(Rule(lhs, rhs))

    def __getitem__(self, nt):
        return self.rules[nt]

    def is_terminal(self, sym):
        return len(self.rules[sym]) == 0

    def is_tag(self, sym):
        return all(self.is_terminal(s) for r in self.rules[sym] for s in r.rhs)

class EarleyState(object):
    def __init__(self, rule, dot=0, sent_pos=0, chart_pos=0, back_pointers=[]):
        self.rule = rule
        self.dot = dot
        self.sent_pos = sent_pos
        self.chart_pos = chart_pos
        self.back_pointers = back_pointers

    def next(self):
        return self.rule[self.dot] if self.dot < len(self.rule) else None

    def is_complete(self):
        return self.dot == len(self.rule)

    @staticmethod
    def init():
        return EarleyState(Rule('<GAM>', ['S']))

class Chart(object):
    def __init__(self, length):
        self.entries = [ChartEntry([]) if i > 0 else ChartEntry([EarleyState.init()]) for i in range(length)]

    def __getitem__(self, i):
        return self.entries[i]
    
    def __len__(self):
        return len(self.entries)

class ChartEntry(object):
    def __init__(self, states):
        self.states = states

    def add(self, state):
        if state not in self.states:
            self.states.append(state)

    def __iter__(self):
        return iter(self.states)

class EarleyParse(object):
    def __init__(self, sentence, grammar):
        self.words = sentence.split()
        self.grammar = grammar
        self.chart = Chart(len(self.words) + 1)

    def predictor(self, state, pos):
        for rule in self.grammar[state.next()]:
            self.chart[pos].add(EarleyState(rule, dot=0, sent_pos=state.chart_pos, chart_pos=state.chart_pos))

    def scanner(self, state, pos):
        if state.chart_pos < len(self.words):
            word = self.words[state.chart_pos]
            if any((word in r) for r in self.grammar[state.next()]):
                self.chart[pos + 1].add(EarleyState(Rule(state.next(), [word]), dot=1, sent_pos=state.chart_pos, chart_pos=(state.chart_pos + 1)))

    def completer(self, state, pos):
        for prev_state in self.chart[state.sent_pos]:
            if prev_state.next() == state.rule.lhs:
                self.chart[pos].add(EarleyState(prev_state.rule, dot=(prev_state.dot + 1), sent_pos=prev_state.sent_pos, chart_pos=pos, back_pointers=(prev_state.back_pointers + [state])))

    def print_chart(self):
        for i in range(len(self.chart)):
            entry = self.chart[i]
            # Format the string for the current input position
            if i < len(self.words):
                current_input = f"{''.join(self.words[:i])}['{self.words[i]}']{''.join(self.words[i + 1:])}"
            else:
                current_input = f"{''.join(self.words[:i])}[]"

            print(f"({i}) \"{current_input}\"")
            
            for state in entry:
                # Print the details of each state, including the rule and the dot position
                lhs = state.rule.lhs
                rhs_left = ' '.join(state.rule.rhs[:state.dot])
                rhs_right = ' '.join(state.rule.rhs[state.dot:])
                rhs_string = f"{rhs_left}. {rhs_right}".strip()
                print(f"\t [{state.sent_pos}] {lhs} -> {rhs_string}")

            # Check for acceptance
            if any(state.is_complete() and state.rule.lhs == 'S' for state in entry):
                print(" ACCEPTS")


    def parse(self):
        for i in range(len(self.chart)):
            for state in self.chart[i]:
                if not state.is_complete():
                    if self.grammar.is_tag(state.next()):
                        self.scanner(state, i)
                    else:
                        self.predictor(state, i)
                else:
                    self.completer(state, i)
            self.print_chart()  # Print chart after each position

    def has_parse(self):
        for state in self.chart[-1]:
            if state.is_complete() and state.rule.lhs == 'S' and state.sent_pos == 0 and state.chart_pos == len(self.words):
                return True
        return False

    def get(self):
        def get_helper(state):
            if self.grammar.is_tag(state.rule.lhs):
                return Tree(state.rule.lhs, [state.rule.rhs[0]])
            return Tree(state.rule.lhs, [get_helper(s) for s in state.back_pointers])

        for state in self.chart[-1]:
            if state.is_complete() and state.rule.lhs == 'S' and state.sent_pos == 0 and state.chart_pos == len(self.words):
                return get_helper(state)
        return None

def main():
    grammar = Grammar()

    print("Masukkan aturan grammar dalam format 'LHS -> RHS1 | RHS2' (masukkan 'END' untuk selesai):")
    while True:
        rule_input = input("Aturan: ")
        if rule_input.strip().upper() == 'END':
            break
        lhs, rhs = rule_input.split('->')
        lhs = lhs.strip()
        for production in rhs.split('|'):
            grammar.add(lhs, production.strip().split())

    while True:
        try:
            sentence = input("Masukkan kalimat untuk parsing: ")
            stripped_sentence = ''.join([ch for ch in sentence if ch not in string.punctuation])

            parse = EarleyParse(stripped_sentence, grammar)
            parse.parse()
            result = parse.get()
            if result is None:
                print("Kalimat tidak dapat di-parse.")
            else:
                result.pretty_print()
        except EOFError:
            break

if __name__ == '__main__':
    main()


#Rule grammar
#S -> NP VP
#NP -> Det N
#VP -> V NP
#Det -> the | a
#N -> dog | cat
#V -> chased | saw

#String :
#the dog chased the dog
#the dog chased the cat
#the dog chased a dog
#the dog chased a cat
#the dog saw the dog
#the dog saw the cat
#the dog saw a dog
#the dog saw a cat
#the cat chased the dog
#the cat chased the cat
#the cat chased a dog
#the cat chased a cat
#the cat saw the dog
#the cat saw the cat
#the cat saw a dog
#the cat saw a cat
#a dog chased the dog
#a dog chased the cat
#a dog chased a dog
#a dog chased a cat
#a dog saw the dog
#a dog saw the cat
#a dog saw a dog
#a dog saw a cat
#a cat chased the dog
#a cat chased the cat
#a cat chased a dog
#a cat chased a cat
#a cat saw the dog
#a cat saw the cat
#a cat saw a dog
#a cat saw a cat

#

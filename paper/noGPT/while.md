# While

## Contents

[History](#History)

## History

We will visit for now "Revised Report on the Algorithmic Language Algol 60". Later, move to the older sources to see if we could find more information.

## Revised Report on the Algorithmic Language Algol 60

From:

2. BASIC SYMBOLS, IDENTIFIERS, NUMBERS, AND STRINGS. BASIC CONCEPTS.
```
<separator>::=  while
```

4.6.1. Syntax
```
<arithmetic expression> while <Boolean expression>
```
```
<delimiter) :: <operator>|<separator <bracket> <declarator> <specificator>
<operator>::= <arithmetic operator> <relational operator>
Logical operator> <sequential operator>
```
# C

Original from Appendix A of C Programming Language Book. 

```
A.9.5 Iteration Statements

Iteration statements specify looping. 
 iteration-statement:
 while (expression) statement
 do statement while (expression);
 for (expressionopt; expressionopt; expressionopt) statement

In the while and do statements, the substatement is executed repeatedly so long as the value of the 
expression remains unequal to 0; the expression must have arithmetic or pointer type. With while, the 
test, including all side effects from the expression, occurs before each execution of the statement; with 
do, the test follows each iteration.


In the for statement, the first expression is evaluated once, and thus specifies initialization for the loop. 
There is no restriction on its type. The second expression must have arithmetic or pointer type; it is evaluated before each iteration, and if it becomes equal to 0, the for is terminated. The third expression is evaluated after each iteration, and thus specifies a re-initialization for the loop. There is no restriction on its type. Side-effects from each expression are completed immediately after its evaluation. If the substatement does not contain continue, a statement 

 for (expression1; expression2; expression3) statement
is equivalent to 
expression1;
while (expression2) {
 statement
 expression3;
}

Any of the three expressions may be dropped. A missing second expression makes the implied test 
equivalent to testing a non-zero element.
```

## VPL

It would be nice to map the "while" to the Antikythera mechanism (100 BCE) and Jacquard's loom machines. The intuition is that if these machines could be described
in terms of Vectors or differential equations or VPL. We could have another link betwen a physical realization and programming semantics. 

### References

- "Revised Report on the Algorithmic Language Algol 60" (1962) https://www.algol60.org/reports/algol60_rr.pdf
- Edsger Dijkstra's "Go To Statement Considered Harmful" (1968)
- Ada Lovelace's notes 
- Ancient Algorithms/Al-Khwarizmi

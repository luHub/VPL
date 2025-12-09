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

## Ada Lovelace's notes

I could not see a "while", here.  

## Antikythera mechanism

I am too lazy to check for a while here... 

## Jacquard's loom machines. 

I am too lazy to check for a while here... 

## Realization 

Why did not anyone mapped this already? that would had save me a lot of time. 

## Periodic Function




## A VPL "while"

After a careful analysis a "while" goes in circles just as a feedback loop or a phasor until a halting condition is reached. 
```
while(expression){ statement }

   expression => (Condition) 
   statement  => (Execution block) will this ever act on the condition?) YES/NO/DW/DC -> Don't care

Remarks: 
Solution one: you are either in the condition or you are in the statement
Solution two: You are in both...

So for VPL, while loops will be in line with "solution one".

For solution two, we will introduce another reserved world a new one called "Phasorial Control Activaton" or "phont" because I am not going to to steal words anymore.
We will research on this later.

For approach 1:
-Create a matrix representation of the 
path. Condition-Execution-Condition-Execution...
-Create a matrix representation for control 

Pictorially. I have analogies but... One is the road, the other the car... 

```


### References
- "Revised Report on the Algorithmic Language Algol 60" (1962) https://www.algol60.org/reports/algol60_rr.pdf
- Edsger Dijkstra's "Go To Statement Considered Harmful" (1968)
- Ada Lovelace's notes 
- Ancient Algorithms/Al-Khwarizmi

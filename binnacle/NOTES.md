# NOTES

A section on notes and ideas

## Notes

## Back to VPL

the first paper should be humble an incomplete as LLMs start hallucinating after some iterations which is kind of expected. The PoC using LLMs give some structure, but full of incoherence. So now, even with not the best English a human version written by me will take place.

### Abstract

A vector space framework for programming is explored to act as a bridge between abstract programming semantics, a programming language, and physical implementations such as analog, digital, and quantum circuits. The idea in the long term is to know which parts or algorithms are better suit to execute as software or hardware. Using the same framework, mathematical model, called that we call VPL for short of Vector Phasor Language. We envision an model that runs on a vector evolution machine VEM. and another goal is to explore new paradigms outside of von Neumann architecture for hardware design. From a knowledge organization perspective this is a mixture of dynamics systems, abstract semantics and quantum realizations. 


### Introduction 

The exercise to transform abstract statements to VPL will start in a program representation in Backus naur form (BNF) and move to a set of rules statements, control and data into 3 different vector spaces. The model of computation has M matrix that acts as a "connection board" between statements, a matrix D which holds a data vector space and a matrix C which holds the control structure. In this model. This model should work with the rules of linear algebra, and should be compatible with circuits mappings. So we could ask what is a "While"
on a circuit is an oscillation, a phasor, a jump in Matrix M which acts as a wiring mechanism. 

#### VPL computational model for assignments

we won't know how this model will look like after mapping all the semantics necessary so we will start by this definition:

```
{M,C,D,A} 
```

Using 4 vector spaces, one for the program structure called M which acts as a connection map, one for control called C, one for data values called , and one called A for the statements.


Now we need recall the definition of a statement. 

...



## Back to Operational models

The shape of different teams regarding software applications and infrastructure cannot be divided in departments as it ends up splitting both. Now infra does not know until late stages what is running and development don't know where is running. This is much worst in Cloud Environments where ignorance is paid when engineers develop their own way of what could had been achieved with a cloud vendor offering. 

Both mindsets are different but whay I would like to suggest is an operational model where we have

'''
(Devs)---(Dev/Infra/Ops)--(Sys/Infra admins) 
<---------- Team Dev ----><--- Team DevOps--->
'''

Having a human bridge which have access to both things. The advantage of this is that any domain problem will have a immediate design towards infrastructure. Any issue at infra will be solved faster, and there are no expensive boundaries. 

Thing is a software engineer must be capable to grasp a basic or medium proficiency on systems.

On the other hands, SRE, Administration, patching, updates, etc, are proper task of a system admin. You can't build applications and at the same time understand property design specifications. 

This model although we have a person in the middle is more cost effective than waiting 1 week for and admin to do something on behalf of another person without any context. Design with tickets is a painful slow process, where people are completely detached and accountability does not exist. 

Also in cloud environments code is splited around
more than just one programming language and one repository. 

The bridge person can tackle normal day by day tickets, but can have deep expertise and knowings about the environment and the people there. Is possible that this person sometimes spend more time on CICD or Cloud terraform files but if you want things in days instead of weeks is the right way to go. Also people will know him, system people will know what is going on. The most valuable thing here is trust, also this person could put a stop or go on early stages of design phases. Example: Solution A, sounds good but will cost a lot to maintain in the cloud... better use this... and that saves a lot of effort. 

Another advantage is that when a sys. admin goes on vacations there is a pull of people to keep things running and know how to deal with critical failures. Getting a much better busfactor.

Desicions regarding infra are not blind because people will know and understand what they are running. 

## Back to VPL

After a small journey into cloud computing to be able to deal continue my line of thinking in soft^2 applications back to VPL.

while toying and writting a non-done paper. There are some insights.

- M as a diagonal or other matrix of 0s and 1s checks.
- C as the control statement matrix checks
- D as the data vector space matrix checks

So right now we could write a small non-iterative program. "make x = x+1 5 times 

```
0:x=x+a
1:x=x+b
2:x=x+c
```

So write the matrix M,C and D. Later we could add matrix C using a while loop. 

1) 5 steps represented in M.one after the another 
2) Find Operators for x=x+a 
3) Define Control Matrix
```
x' = (operator) x + (operator) a
x'' = (operator) x + (operator) b
x''' = (operator) x + (operator) c

-> Use affine transformation Ax+b in matrix form for each statement:

x'   = Ix+a
x''  = Ix+b
x''' = Ix+c

V = [ v(0) v(1) v(2)  ]T with only one c active at a time

v(0) = [ 1 0 0 ] ....

M = [0 0 0, 0 1 0,0 1 0]

D = [x' x'' x''']

v(1) = M V(0) -> x'
v(2) = M v(1) -> x''
v(3) = M v(2) -> x'''


```




## Software another approach 

Looking at AI agentic design, is a practice is a small shift in applications design, from an artisan perspective, just another tool in the shelf, is not direct competition to a classical software mindset, is a shift in mindset that could ease design and operation of certain types of applications or systems making them more "soft" what I mean is that, is kind of silly to reject the power of logic, presicion, soundness and completeness obtained using programming language grammars and thinking logicaly ahead. But for sure, there are a bunch of applications that do not require that, those are applications could benefit from these approach, a more data driven one. For example: A workflow observer that suggest to a user the most optimal course of action to accomplish a non critical task, is not like the application is bounding the user to a series of predefined steps, but just influence desicion making, then a suggestion is up to the user to consider it right or wrong, so as long as the power of taking the choice is the right party, is more flexible to sacrifice presicion for guidance, as it is easier to maintain. At the end it boils down to use the right tool for the right purpose, to obtain a another level of "soft".      

Can this more-soft applications compete with classical applications. Well, Nope, I think they are here to stay in their niche and complement classical software ones. How do you know your application is not "more-soft" quite simple check if is there is an explosion in complexity that typically happens when you are using the wrong tool, approach, or yourself is wrong. Some developers even feel happy about this, converting a solution into an intellectual challenge. Is quite hard to define this, because is not only one thing is wrong, but is a collection of wrong doings both at organization and personal level. Classical software creation is also prone to this mistake when a developer or engineer use the wrong level of abstraction and make the problem more complex, not because of lack of knowledge but lack of moderation, One explanation could be that he or she needs to prove to the world or them selves that are smart and important, I call this reflextion of oneself into the code. So yeah, again pick the right tool for the right job. 

## Software another approach

What I am trying to explain is that Software engineering requires a set of social/technical skills that are obtained by doing, it is a personal experience. The mindset of an artisan or artist does not couple with linear or exponential productivity fallacies created to appeal desires for immediate wealth. 

There are a tons of books, tons of videos, tons of opinions but your own proper interpretation is the key. 

## Software another approach 

Intuition wins over logic as logic will come later. Intuition is the compass to navigate infinity, with logic we could go from A to B, But knowing where to go
does not belong to pure logic as science is totally incomplete and there is a lot there to discover. As part of this approach we start on the side on the things that cannot be measured, cannot be predicted, cannot be seen, and use our intuition to navigate that. 

In a very naive classification there are two types of programmers, the craftman (who belong) and the artificials (who dont belong). The later group always suffers on their own demise... trying to belong to a place they do not belong, this group lacks or supress any intuition which they won't have in the first place and just use metrics, kpis and other means to measure on what they consider success. Detail is that you can't measure what you don't amd can't understand. Later, they try to mimic or excel imitating, they become lost or useless in the advent of the smaller change in the field landscape. This profession is about sculping systems, LLMs, IDEs, and languages are just tools, just like in any craftmanship. If you are in this group, consider if you really like this, or you just want to work in the digital version of blockbuster to earn lots of money. If money is your main driver, start in the business sector where you trully belong.

For the first group, the craftman, is possible to flow like water, using the intuition and inspiration to create systems. This approach considers 
exploring intuition first and then the rational part later. Start with an idea, this will take you 10 years, so no rush, from your idea do the smallest effort possible to write a solution, work in very small understandable deltas, and do a 3 or 4 levels deep exploration of what the code is doing in every step. Now, every time you dive down, read and study what is happening, might take you a lot of time but there is not rush. 


## Software another approach 

We will use for VPL as Design Methodology:

Software design in an act of understaing a complex problem and find a solution given a set of constraints. Now a days the prefered approach is from an engineering starting point, mostly coping and fitting ideas from other more mature engineering practices. This approach has re-written and re-applied concepts that might work
to some extend with certain level of success in other contexts with the illusion that they will work on Software. Software is not only an engineering, is also science, is something else, it has a certain unique mix that make it different from classical engineering disciplines, on top of that is a young engineering, so is expected that how we reason about it will change in the years to come.

I would like to propose a different approach to do software. Starting this journey at a philosophical level to deal with abstractions. Is not that I don't
agree with the current body of knowledge, is more that it is incomplete, and this is just another branch of exploration. 

Conways law states that "the structure of any system a company designs will reflect the organization's communication structure". I have seen this pattern 
and also the other way around, so if this happens at "organizational level", I would like to explore what might happen at a personal level. In other words, 
is the well beign, mind clarity, complexes, emotions linked to how code is written? Is bold to assume without data that "Controlling people will write code that has a lot of control", "Ignorant people will write code that will miss some important considerations", but seems to be a feasable cause effect scenario.

I would prefer for now to map philosophy to design, but at very abstract level, and see if we can create something else, just for fun. We need to come with new terms, new vocabulary and free our mind from bias of re-using re-writting definitions, again just for fun. 

### Case example: The influence of "psyche" in software design: Use case Temple OS"

To understand what is considered "normal" in the surface, a good starting point is to consider what is not normal. There are 
few publicly know studies in the influence of the "psyche" in software design, because is considered an "Engineering", I think this is not entirely true.

Temple OS was developed by Terry Davis who according to Wikipedia had a history of mental problems. Therefore is interesting to point out the reflection of those issues in the final product that he made by himself called Temple OS. Now, "normal" people or how they called themselves "Sofware Engineers" or "Software Architects", labeled as "normal people" still had triats of personallity that might influence the way they conceive, and create solutions. It is worth to explore that the real ingenous part of this discipline relies exactly in this point a "personality reflection" and that reflection to the code is what actually distinguishes a "good" from a "terrible" implementation. Also this could explain why the best companies, the best software are the ones with only the vision of one mind (less reflection) that is clear and presice. So the failure of "commetee solutions" in software which create mediocrity only acceptable in low competitive markets or for companies that are bailed out by tax payers. 

My prediction and opinion that now a days, with the advent of LLMs the exercise of reflection will get lost if not used correctly, which will create an entire body of shallow applications and a enormous body of shallow "developers" and enormous amounts of useless code.  

### Recipes

- Avoid going directly into vendor architectural design patters. They are good but focused solely on creating a solution based on their offerings.

- Go first for simple profs of concept. carefully defining what you need now, towards an end goal. 

- Write PoC code togheter with the specification, as writing the PoC will bound the specification to a more presice language. When I say write, you, not an LLM until you bound with the code. 

- Code is a reflexion of your thinking process, influenced (need research here) by a person unconscious,by your shadow (if you are into Jungian school) a person that thinks that working more will create more value, will end up in a writing processes that needs people to work long hours to work with. A disorganized person will write code that is difficult to navigate, a person that has fear to share knowledge will write obscure code that only understable to that person, and obsessive compulsive order person will create such much order that the code will be difficult to bend, disguising it as "clean code" in a total negation of an unhealthy metal issue, the "code becomes the shadow". Code is a reflexión of the person writing the code, as solutions reflects the shape of organizations.

- Bonding with code suppose an exercise that needs years of preparation and practice, it could start in different places. From physics, solid state devides, electronics, CPUs, and finally code, and writing a lot of code. But there in another process that starts in philosophy, mathematics, and language studies. One approach path is abstract and the other is concrete. They touch eventually in a frontier when a proper language transforms into 0s and 1s. But how you approach and abstract solution is a very abstract process that needs a very prepared mind. lack of knowledge in general will impact solutions. The more a "programmer" reads, study, practice the more rich of options will have to define a solution. An empty mind will create an empty solution. In my opinion this is why people in this profession burn out, their intellectual limit,lack of courage, lack of clarity, lack of skills in general get exposed as wrong paths are choosed in the design process. 

- All the modern design practices ended up adding more to the process than actual value. Don't follow them blindly over time. what worked on a time frame might not work in another one. Do not avoid the mental challenge to adapt over time, to challenge control or status-quo,even adapting by laziness is preferred asking why really need to do this?

- I think is good that code reflects the mindset of a programmer, because if code is a reflection of your thinking process then the more different personalities the more rich code that is created. In my opinion innovation comes from the thinking process that gets better as more different mindsets solve a problem, individually and darwinism will do the rest. If we make of everything a standarized process then innovation is lost. 



## Later on VPL
Later with VPL we will explore a frontier between external and internal mediums. modelling the external part as chaos, but understanding how the internal one react to it.

## Reading Backus,Dijkstra

I kind of share some Backus mindset regarding equational reasoning to certain extent. Mine is more vectorial reasoning. time to read more 

## Thoughts

There are some points of views that worth to explore, going back to Edsger Dijkstra that might bring some insights to VPL.  

let's check "A Primer of ALGOL 60 Programming"

## Thoughts

Once VPL works, I would like to create an hybrid architecture that each part is the best for different parts, combining analog,digital and quantum togheter.
Doing good benchmarking between different implementations for each component. Would be fun. 

## Action plan

For 0.0.3 we will explore the for loop. but also we will explore semantically the while and the for. this will give us an interesting framework to waste as much time as possible in the most creative ways... I am joking... not joking... you will never know...

## Thoughts 

The amount of bullshit generated for V0.0.2 is astonishing but enterteining. Now the fun part will be to produce some usefull result
and start all over again for V0.0.3. So we will expand the compiler, now, here are my actual 2 cents on this... see, we start
from the compiler with a sensitive grammar "C language" and we go from there.

## More next next steps 2025_10_X

As the master paper growths, it revealed a structure, that it is, the information needs a word by word examination.
But we will start journey from the compilers code, and later fix the mathematical framework. 


## Next steps 2025_10_X

I will focus on the compiler for now and do a full FFT implementation, first by adding testing to all the parts of the compiler.
Once this works. Proof by mathematical testing all the sections.  Once that works create another model adding observability to VPL.

## Obsevation Matrix (Posponed for now) 2025_10_X

Wild Idea: Not implemented. Once the framework is completed create an "Observation Matrix". Now, think of a "System" that could
"observe" reallity and reallity depicted by VPL, well a vectorial representation given by VPL of an algorithm, later do "inference" about the "observation" based on some "observability mechanism". But this might complicate the model we could do it as an expansion model later. Once all is verified and corrected, we will add this in future versions.

## Hallucinations and fun 2025_10_X

Adding some primitive blocks to VPL, if all this wrong it would be fun to disprove it. If is all right, this will start to get spooky when I add more direction into the unknown. if is right/wrong would be a very good experience to split both

## Does a while loop has noice 2025_10_16

This is one of the questions that would be fun to answer, "the noise of semantics" when transformed to different physical implementations. 
As VPL evolves we could do some metrics to answer this question. 

## Specialization vs Generalization 2025_10_16

The quest for discovery of new things could be impacted with this mythic question about Specialization vs Generalization.
  
"Jack of all trades, master of none" vs "If you only got a hammer, everything is a tool".

In my opinion, the flaw becomes not in one or another but placing them as opposing forces, which given time
constraints, classification, categorization, and infinite amount of knowledge to be harvested it sounds a promising way
to favor one or the other. At the end is about infinite knowledge vs time. It is tempting to only focus on one thing, but
one thing disconnected from all the other things is worthless. 

So we should see specialization and generalization as expansion and contraction, or as a cycle. In that sense the exercise to 
generalize and specialize over and over could act as a pump to extract knowledge, and the setting on how deep and how superficial we
want to go is what will define our success.

VPL migh suffer from this between "opposing" forces in mathematics, physics, and engineering. If is too theoretical there will be no applied purpouse if 
is full of purpose will not haverst unkown knoledge. So if a fun game to play with.

## While Loops 2025_10_11

To understand what we are doing, which most of the time we don't know, a careful analysis of what has been done is needed, in the words of a famous unknown person.. "Do some reading"

So well we started the example with a "while loop" thinking yeah... but w while loop is not as innocent as we think. It required thousand of years of civilization to be useful in the society. But the idea was there for hundred years ago.

- Could we express a while loop in terms of linear algebra? 
- Could we map it to oscillators? 
- What are the benefits and limitations? 
- Could we reason about a while loop differently? 


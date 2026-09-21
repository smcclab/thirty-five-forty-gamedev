---
title: "Week 9: Training the Player and Balancing"
description: "What you need to teach your player and how to teach it, then identifying the variables, dynamics, rewards, punishments and difficulty you will need to balance."
order: 9
toc: true
heroImage: /src/assets/images/photos/stick-maze-level.jpg
heroImageAlt: "A maze level built from coloured craft sticks"
---

A long design workshop, run in your project team. The first half is about
training -- a game cannot be fun if the player does not know how to play it.
The second half is about balance: the variables and dynamics you will have to
tune, the rewards and punishments you give out, and the difficulty you are
aiming for. You leave with a balancing plan for your next sprint.

## Before the workshop

- Review the Week 4 and Week 8 theory.
- Work on your first sprint towards a playable version.
- Continue your first [Developer Diary](/assessments/diary/) entry.

## In the workshop

| Time | Activity |
|---|---|
| 10 min | Activity 1: Scrum |
| 15 min | Activity 2: Learning -- what to teach the player |
| 15 min | Activity 3: Learning -- how to teach the player |
| 15 min | Activity 4: Balancing variables and dynamics |
| 10 min | Activity 5: Balancing rewards and punishment |
| 10 min | Activity 6: Balancing for skill and difficulty |
| 10 min | Activity 7: Balancing approach and plan |

## Recap: learning to play

Good game design teaches the player how to play and enjoy the game. This is
one of the most important concepts in game design: if the design does not
support learning through training, the game will never be fully enjoyed. The
game cannot be fun if the player does not know how to play, and if the
underlying systems are superb but never harnessed by the player, they
effectively do not exist.

This applies at every scale, from the smallest gameplay mechanic to the
largest span of levels and features -- the physical rules of the environment,
the abilities of the player character, the behaviour of enemies, the reward
systems. The game as a whole suffers if these are not taught.

Key areas to teach:

- **Goals and rules.** The player needs to learn early what constitutes the
  core gameplay experience, what the main objectives are, and how to achieve
  them, level by level and overall.
- **The player character.** This is much of the player's interface to the
  world, and it defines their abilities and limitations within the game's
  reality. Teach it early: the sooner the player accepts it, the sooner they
  can suspend disbelief. Changes can come later, once the fundamentals are
  established. In *Tetris* the player needs to know how to rotate, direct and
  drop shapes; in a first-person shooter, how to move, shoot and interact.
  Where the gameplay does not run through an avatar the principle still holds:
  the player needs to know how they can manipulate the virtual world.
- **Physics and scope of the world.** Player actions have little meaning
  unless performed in a defined physical context.
- **Non-player characters.** How to interact with friendly NPCs (keeping them
  friendly may be a challenge in itself), and the abilities, hazards,
  strengths and weaknesses of enemies.
- **Success strategies** available to the player.

### Training approaches

Recommended:

- **Teach by practical example.** Learning by doing works best for most
  people. When a new mechanic is introduced, let the player try it
  immediately, while the lesson is fresh.
- **Positive reinforcement.** Reward players actively when they pass a skill
  test or get through a challenging scenario. Positive consequences make
  players eager to engage.
- **Teach in a safe environment.** Let players comfortably learn the skills
  they need before difficulty ramps up. Lessons at the start of the game
  should be forgiving.
- **Prepare the player fairly.** Ensure they have the right tools and
  knowledge before a skill test they can fail. Lethal encounters are fine, but
  they must be fair; avoid unannounced or unavoidable instant-death traps.
  Where you can, teach skills in a way that players cannot fail, so they can
  focus on practising.

To avoid:

- **Don't start with failure.**
- **Don't taunt the player.**

### Training methods

- **Tutorials and in-game training** are interactive learning experiences that
  introduce mechanics, controls and concepts. Good training is enjoyable and
  effectively invisible. Use it sparingly, don't over-explain, give
  information in small manageable bites, and never use it as a fall-back for
  bad design.
- **Progression.** Gameplay needs to be introduced gradually. Too slow and
  players are bored; too fast and they are confused and frustrated. Getting
  the progression right is key to enjoyment.

### Good design practices

Design the game to *avoid* training where you can: use industry standards,
meet player expectations, allow players to customise controls, don't
over-complicate mechanics or controls, and keep concepts simple and sensible.
If you can't explain it, it's too complicated.

## Recap: balancing game systems

Balancing is the process of making sure the game meets your player experience
goals -- that the system is of the scope and complexity you envisaged, and
that its elements work together without undesired results (Fullerton
p.321--342).

- **Variables** are the numbers that define the properties of game objects:
  the number of players, the size of the playing area, the amount of a
  resource. Changing their values can drastically change how the game plays
  out.
- **Dynamics** are the forces at work when the game is in action. Unexpected
  things happen when a system is set in motion, and combinations of rules,
  objects and actions can create imbalance. You then fix or remove the
  problem, or add a rule to mitigate it.

Two related ideas: **fairness** gives all players an equal opportunity to
achieve the game's goals; **balance** concerns the availability of dominant
strategies or overpowered objects.

- **Dominant objects.** Similar objects should be proportional in strength --
  no single unit significantly more powerful than the others. Provide choices
  through strengths and weaknesses, as in rock-paper-scissors: good at hills
  but poor on corners; a killer move but an Achilles heel; durable but
  expensive. Asymmetric but balanced is difficult to get right.
- **Dominant strategies.** A strategy that is strictly better than all others
  makes the game dull, because the player always chooses the same thing.
  Tic-tac-toe has one, and is boring once you know it. This is not the same as
  a *favourite* strategy, which multiplayer communities develop and evolve
  over time.

Schell's **lens of meaningful choices** (#39): what choices am I asking the
player to make? Are they meaningful, and how? Am I giving the right number --
would more make the player feel more powerful, would fewer make the game
clearer?

### Rewards and punishment

Players want to be rewarded for doing well. Schell's types of reward
(ch. 13, p.212--250): praise, points, prolonged play, gateway (unlocking a new
area), spectacle, expression, powers, resources, status and completion.

Punishment can increase enjoyment: it creates endogenous value (fear of losing
something), makes risk-taking exciting, and makes success more rewarding
because failure is possible. Types: shaming, loss of points (painful, use
sparingly), shortened play (a timer, lives), terminated play, setback to a
checkpoint, removal of powers (tread carefully -- players treasure them; make
it temporary), and resource depletion (money, goods, ammunition, shields, hit
points).

The **lens of reward** (#46): what rewards is my game giving out now, and can
it give others? Are players excited by them or bored? Do they understand them
-- a reward you don't understand is like no reward at all. Are they too
regular? How are they related to one another, and are they building too fast,
too slow, or just right?

The **lens of punishment** (#47): what are the punishments? Why am I punishing
players, and what do I hope to achieve? Do the punishments seem fair, and why?
Could any be turned into rewards for the same or better effect? Are strong
punishments balanced against commensurately strong rewards?

### Balancing for skill

Every player has a different skill level. You can offer difficulty levels the
player chooses, which modify some variables such as hit points; balance
against a *median* skill, which requires extensive playtesting with players of
different skill to find the high and low points; or balance *dynamically*,
adjusting difficulty to the player's skill as they play -- *Tetris* increasing
block speed with score, racing games "rubber-banding" to the player. Dynamic
balancing usually wants to be invisible.

Techniques: increase difficulty with every success; let skilled players get
through easy parts fast; create layers of challenge, such as a score or rating
to beat next time; let players choose a difficulty level; playtest with a
variety of players; give the losers a break, such as extra power-ups.

The **lens of challenge** (#38): what are the challenges in my game? Too easy,
too hard, or right? Can they accommodate a wide variety of skill levels? How
does challenge increase as the player succeeds? Is there enough variety? What
is the maximum level of challenge?

The **lens of competition** (#43): does my game give a fair measurement of
player skill? Do people want to win, and why? Is winning something to be proud
of? Can novices compete meaningfully? Can experts? Can experts generally be
sure of defeating novices?

### Techniques and methodologies

Fullerton's techniques:

- **Think modular.** Most games are a set of interrelated sub-systems. The
  more interconnected they are, the harder to balance, so isolate and abstract
  them: then when you change something you can see its effects.
- **Purity of purpose.** Every component has a single, clearly defined
  mission; nothing exists without reason or with more than one function. Break
  mechanics down into building blocks with a flowchart.
- **One change at a time**, then test, so causes of effects are known.
- **Spreadsheets.** Track everything in one. It is easier to see everything at
  once and to model changes and their effects.

Schell's methodologies:

- Use the lens of the problem statement: define the balance problem before
  trying to solve it.
- Doubling and halving: start with large changes to test the limits and save
  time.
- Train your intuition by guessing exactly: make a best guess and test it.
- Document your model: what is the relationship between variables and
  elements?
- Tune your model as you tune your game.
- Plan to balance: put systems in place that make it easy to change the values
  that will need balancing.
- Let the players do it, to a limited extent -- for example by choosing a
  difficulty level.

## Activities

### Activity 1: Scrum (10 min)

Run a scrum meeting for your team. Each person reports what they did since the
last meeting, what they will do before the next one, and what problems they
are facing.

### Activity 2: Learning -- what to teach the player (15 min)

In your team: what do you need to teach your player so they can play and enjoy
your game?

- What do they need to know about the goals and rules, particularly the core
  gameplay and main objectives?
- What do they need to know about the player character, or their interface to
  the game world -- particularly the controls?
- What do they need to know about interacting with the game world?
- What do they need to know about any non-player characters?
- What are the *essential* things you need to teach, keeping training to a
  minimum?

### Activity 3: Learning -- how to teach the player (15 min)

In your team: how will you teach your player, in a positive, practical, safe
and fair way?

- In what format will you deliver the training?
- When will you deliver it, and how will you manage its pace?
- How will you integrate training into the fun of the game?
- Will the player get a chance to put training into practice immediately?
- How will you use industry standards and meet player expectations?
- Are any of your concepts, mechanics or controls too complex? Can you
  simplify the game to reduce the training required?

### Activity 4: Balancing variables and dynamics (15 min)

In your team, identify what you will need to balance to make the game playable
and enjoyable.

- List all the **variables** in your game. What are the starting values? What
  are the possible values?
- Identify the key **dynamics** you might need to balance. How can rules,
  objects and actions combine to create imbalance?
- Identify any **dominant objects**. This matters most where the player
  chooses between objects -- will they always choose the same one?
- Identify any potential **dominant strategies**. Are there multiple ways to
  play or to solve problems? Are there benefits and drawbacks to each?

### Activity 5: Balancing rewards and punishment (10 min)

In your team, identify and analyse the rewards and punishments in your game.

- List the rewards you give the player. When and how often? Are they useful or
  meaningful? Do they make the player want to keep playing?
- What will you need to consider in balancing them -- timing, type, size,
  usefulness, impact on player power? Can you add more?
- List any punishments. Why are you punishing the player? Do they enhance the
  game? Will they seem fair? Could you make them rewards instead?

### Activity 6: Balancing for skill and difficulty (10 min)

In your team, decide your approach to difficulty.

- One difficulty level, or can the player choose?
- Will the game stay the same difficulty or increase over the 15 minutes of
  play?
- What determines difficulty in your game? Look back at your variable list
  from Activity 4 -- which can you change to alter difficulty?
- How will the rewards and punishments from Activity 5 affect difficulty? Does
  getting them make the game easier or harder?
- How difficult do you *want* the game to be? What is your target level of
  challenge, and how will you challenge the player?

### Activity 7: Balancing approach and plan (10 min)

In your team, agree an approach and write it down.

- Based on Activities 4--6, what will you need to balance?
- How important is balance in your game, and how complex will it be -- are
  there many variables, rewards and so on? What are the risks of not balancing
  well?
- What approach will you use?
- When will you balance? What is ready to balance now, and what has to wait on
  implementation?
- How can you implement the game to make balancing easier? What tools will you
  use -- a spreadsheet, for instance?
- Who is responsible for balancing?

Write up the plan and incorporate it into your next sprint.

## After the workshop

- Review the Week 9 theory.
- Work on your sprint towards a playable version.
- Submit your first [Developer Diary](/assessments/diary/) entry.

## References

- Fullerton, *Game Design Workshop* -- p.321--342 (balance).
- Schell, *The Art of Game Design* -- ch. 13, p.212--250 (balance, rewards,
  punishment, and lenses 38, 39, 43, 46 and 47).
- Kremers, *Level Design: Concept, Theory, and Practice* (2009) -- ch. 2
  (training).
- Rouse, *Game Design: Theory & Practice*, 2nd ed. (2005) -- ch. 7
  (training).

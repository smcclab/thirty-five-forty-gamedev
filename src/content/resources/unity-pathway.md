---
title: "Unity Pathway"
description: "The self-paced Unity Junior Programmer Pathway that runs through the first half of semester, and how each unit feeds the prototype assessments."
order: 2
toc: true
heroImage: /src/assets/images/photos/block-layout.jpg
heroImageAlt: "Coloured paper blocks laid out as a platformer level"
---

The engine skills in this course are taught through Unity's own
[Junior Programmer Pathway](https://learn.unity.com/pathway/junior-programmer),
worked through in your own time. There are no classes for it. You start in week
1 and complete roughly one unit a week through to week 6, while the
[workshops](/workshops/) develop the design of the game you are building and
the [theory decks](/lectures/) give you the concepts to analyse it with.

This is the part of the course that most often goes wrong. The pathway is
self-paced, nothing chases you, and the prototype assessments assume the skills
are already there. Falling two units behind in the first month is the single
most common reason students struggle in the second half of semester.

## The units, week by week

The pathway's project course *Create with Code* is the core. Each unit is four
lessons plus five challenge tasks, and takes roughly four to five hours.

| Week | Pathway unit | What you can build afterwards |
| --- | --- | --- |
| 1 | Getting Started; Unit 1 --- Player Control | A scene with a player object that moves from keyboard input, with a camera that follows it |
| 2 | Unit 2 --- Basic Gameplay | Objects that spawn, move, collide and are destroyed; the beginnings of a game loop |
| 3 | Unit 3 --- Sound and Effects | Audio, particle effects and animation triggered by gameplay events |
| 4 | Unit 4 --- Gameplay Mechanics | Waves, powerups, enemy behaviour and physics-driven interactions |
| 5 | Unit 5 --- User Interfaces; Next Steps | Score, lives, timers, buttons, start and game-over states |
| 6 | Catch-up and consolidation | Finishing the prototype and writing the proposal |

Each unit ends with a challenge --- *Plane Programming*, *Play Fetch*,
*Balloons, Bombs & Booleans*, *Soccer Scripting*, *Whack-A-Food* --- in which
you fix five deliberate faults in a working project. The challenges are where the learning
sticks; do not skip them.

The pathway also contains a set of standalone tutorials beyond *Create with
Code*. They are optional, and several of them are useful later in the group
project.

## Turning the tutorials into your own prototype

The pathway teaches you a game that is not yours. The assessments want a
prototype of the game *you* designed in the workshops. In 2024 the bridge
between the two was a sequence of short lab exercises that re-did each
tutorial's technique on your own concept:

| Lab | What you build on your own concept |
| --- | --- |
| Lab 2 --- New project with primitives | A background plane, a primitive player, and a camera placed for your game type (top-down, side view or isometric); primitive enemies, obstacles and projectiles, distinguished by shape and material |
| Lab 3 --- Player control | A player controller with movement driven by player input, with the constraints your design needs |
| Lab 4 --- Basic gameplay | Object movement, spawning, collisions and destruction --- enough for the core loop to be playable |

Those three labs, plus the workshop design activities, are exactly what the
[Prototype Progress](/assessments/progress/) assessment asks you to have built
by week 4. The [Game Proposal and Prototype](/assessments/proposal/) is a more
developed version of the same prototype, with interface work from unit 5 and
week 5's theory added. It is fine --- normal, even --- for the concept to have
changed between the two.

Everything in these prototypes is **primitives only**: no assets, free, paid or
self-made. Materials are allowed, textures are not. See the
[asset policy](/policies/#assets).

## Planning your project

Unity's *Create with Code* project design document is a useful planning
template and follows the same six-part structure as the units: player control,
basic gameplay, sound and effects, gameplay mechanics, user interface, and
anything else. Filling it in forces you to say, in one sentence each, what the
player controls, what appears and from where, what the goal is, and what ends
the game. If you cannot fill it in, the concept is not yet a design.

The same document carries a milestone table. Setting five milestones with dates
across weeks 1--6 is the simplest way to keep the pathway from slipping.

## How the pathway is assessed

In 2024 the pathway was not marked directly. It was assessed indirectly,
through the prototypes it lets you build and through the prototyping process
reports that describe your Unity activity week by week.

The 2023 offering did assess it directly, as five weekly *Game Labs* worth 2%
each in weeks 2--6: each unit's four lessons and five challenges submitted as
separately named commits to a GitLab repository, with comments in the C#
describing what each step added. That item was dropped for 2024.

:::info
Whether the next offering marks the pathway directly is **TODO**. The 2023
approach gives students a reason to keep pace and gives staff visibility of who
has fallen behind; the 2024 approach costs less to mark.
:::

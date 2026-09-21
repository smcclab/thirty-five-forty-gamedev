---
title: "Week 5: Interface Design"
description: "Choosing a viewpoint, designing a keyboard-and-mouse control scheme, mapping information to channels, and planning the feedback your game gives the player."
order: 5
toc: true
heroImage: /src/assets/images/photos/interface-sketch.jpg
heroImageAlt: "A paper sketch of a game interface with panels and a character face"
---

Five short design exercises that take your prototype from "a set of rules" to
something a player can actually see and operate: the camera, the controls,
what the screen tells them, and what the game says back when they act.

## Before the workshop

- Review the Week 4 and Week 5 theory.
- Keep working on your prototype, physical and digital: add your formal
  details, then refine.
- Continue the Unity Junior Programmer Pathway: Unit 4 -- Gameplay Mechanics,
  then Unit 5 -- User Interfaces and Next Steps.
- Keep documenting your progress, and submit [Game Prototype
  Progress](/assessments/progress/).

## In the workshop

| Time | Activity |
|---|---|
| 15 min | Activity 1: Choose your viewpoint |
| 20 min | Activity 2: Design your control scheme |
| 10 min | Activity 3: Communicating information to the player |
| 20 min | Activity 4: Designing your interface |
| 15 min | Activity 5: Feedback in your game |

## Recap: the game interface

The interface between the player and the game covers both directions
(Fullerton p.254--266):

- **Input** -- devices and control schemes.
- **Output** -- the camera viewpoint on the game environment, and the visual
  display of game status and of the controls the player uses to interact with
  the system.

Controls, viewpoint and interface work together to create the game experience
and to let the player understand the system and have agency within it.

### Selecting viewpoints

| Viewpoint | What it affords |
|---|---|
| Overhead | Looking directly down on the game world. A clear view of terrain; useful for strategy and tactics. |
| Side | Looking side-on. Side-scrollers, platformers, arcade games. The player controls units in two planes; focus on puzzles. |
| Isometric | A 3D space with no linear perspective. A "god's eye" view; strategy, construction and role-playing games. |
| First-person | Through the eyes of a character. Creates immediacy and connection, and limits knowledge of the game state. |
| Third-person | Follows a character without being inside their view. A detailed view of the character's action; adventure, sport. |

Different viewpoints give different degrees of access to the state of the
world and different relationships to the character and objects, so the choice
is a formal *and* dramatic design element. Consider prototyping with more than
one. Ask: should the player feel extremely close to the character, sharing
their sense of movement and their lack of knowledge? Or stay close but
slightly outside, seeing more of the environment and picking up clues the
character cannot see? Is there no character in your game, or no world -- and
if so, what view makes the most sense?

### Control schemes

Controls carry player input into a digital game, and advances in control
systems have brought new audiences to games -- the immersive play of VR
headsets, the simple intuitive play of phones and tablets. You need to
understand the capabilities of the controller for your platform, and design
in conjunction with the interface. Start from your list of procedures: each
has to be translated into a digital control. Highly detailed controls may need
grouping under a menu or other visual device.

Once you have decided how the controls work, **make a control table**: list
the controls and, next to each, the game procedure it is attached to. Very
complex games may need several tables, one per game state -- a new state
exists each time the controls change (driving a car, flying a plane, riding a
bike) -- but keep the controls as similar as you can between states.

Designing controls, like designing games, is iterative: you only know whether
they work by testing. The goal is to make them effortless. Players do not want
to think about the controls; they should feel intuitive. Too many controls
frustrate the average player. Expert players may want detailed or custom
controls, but not at the cost of alienating less experienced ones.

### Interface design

The interface is how information about the game state and the player's options
is communicated: points and progress, the status of units, communication with
other players, perpetual choices, special opportunities for action. How will
you fit this in or around the main view? Make it as easy to understand as
possible -- ideally fresh and innovative, but familiar and intuitive.

*Form follows function*: the design of an object must come from its purpose
(Louis Sullivan, 1896). The formal elements inform the interface and control
design. Do not design the interface first; it comes from the gameplay.

### Channels of information

Schell ch. 15, p.268--295:

- **List and prioritise information.** There is a lot of it, and not all of it
  is equally important.
- **List channels** -- ways of communicating a stream of data: top-centre of
  the screen, the avatar, sound effects, music, the border of the screen,
  marks on enemies, word balloons over heads. List all the channels you might
  use.
- **Map information to channels**, by instinct, experience and trial and
  error. Playtest, remap, repeat.
- **Review your use of dimensions.** A channel can have several dimensions
  (colour, size, font). Using dimensions to reinforce the same information
  makes it clearer; using them for different information can be elegant.

### Effective interface design

- **Visualisation.** Players often need to process a lot of quantitative
  information very quickly. Visualise it so they can read their status at a
  glance, and use cultural expectations to cue meaning -- natural mapping. An
  arc, like a petrol gauge, reads left to right as empty to full; a rising
  bar, like a thermometer, reads up and down as rising and falling.
- **Grouping features.** Group similar features together visually -- combat
  features, health information, communications -- so the player always knows
  where to look.
- **Consistency.** Keep features in the same place between screens, and follow
  the standards and expectations set by similar games.
- **Feedback.** Let players know their action was accepted: did it register,
  did it work? Aural feedback is very effective for a responsive interface.

## Activities

### Activity 1: Choose your viewpoint (15 min)

Working individually (5 min), think about your core gameplay and your player
experience goals.

- List the possible viewpoints you could use.
- For your game, what are the benefits and drawbacks of each?
- How well does each support your desired experience and gameplay?
- Which is the best fit, and why?

In your table group (10 min), go around the table. Explain your chosen
viewpoint and your reason, and for each person give feedback on whether the
chosen viewpoint is well suited to their core gameplay. Note the feedback you
receive.

### Activity 2: Design your control scheme (20 min)

Working individually (10 min):

- List the procedures in your game.
- Draw or list the control scheme. **You can only use a keyboard and mouse.**
- Which keys and buttons will you use, and what will each do?
- How complex is the scheme? Will it be hard for the player to learn or
  remember?
- Do you need different controls for different modes or states?

In your table group (10 min), briefly compare how many procedures and controls
each of you has. Have you used the same keys or buttons for similar
procedures?

### Activity 3: Communicating information to the player (10 min)

Working individually, list all the information you need to communicate to the
player through the game -- points and progress, the status of units, the
choices they can make, opportunities.

- What do they need to know at any point in time?
- What is the most important information to communicate?

Then list the channels you might use: top-centre of the screen, the avatar,
sound effects, music, the border of the screen, marks on enemies, word
balloons over heads.

### Activity 4: Designing your interface (20 min)

Working individually (10 min), draw an initial design for your game interface.
Consider visualisation, cultural expectations and consistency. Where will each
piece of information or option be displayed, and how? Imagine playing your
game with this interface -- is anything missing?

Working in pairs (10 min), take turns to show and explain your design.

- Is it easy to understand, use and remember?
- How is the visualisation, the grouping, the consistency?

Note the feedback you receive.

### Activity 5: Feedback in your game (15 min)

Working individually (10 min), create a list of the feedback your game gives.

- What types of feedback do you need to communicate?
- Is each best communicated aurally, visually, or both?
- Where, when and how will you communicate it?
- Add the feedback to your interface design.

In your pairs (5 min), discuss your plan. What feedback is essential? How well
does it integrate with your interface design?

:::tip
Photograph or save the output of each activity. It is evidence for the
[Game Proposal and Prototype](/assessments/proposal/), whose interface
section asks you to explain and justify exactly these decisions.
:::

## After the workshop

- Review the Week 1--5 theory.
- Keep working on your prototype.
- Complete the Unity Junior Programmer Pathway: Unit 5 -- User Interfaces and
  Next Steps.
- Start filling in the Game Proposal and Prototype template, and **bring it to
  the Week 6 workshop**.

## References

- Fullerton, *Game Design Workshop* -- p.254--266 (interface design,
  viewpoints, control schemes, effective design).
- Schell, *The Art of Game Design* -- ch. 15, p.268--295 (channels of
  information).

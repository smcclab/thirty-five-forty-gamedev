# COMP3540 source materials

A survey of `../comp3540-materials/` (the OneDrive copy of the 2023 and 2024
offerings, ~13GB, 184 files, not in this repo) and what it would take to turn
it into this site. Written 2026-09-21, before any content conversion.

The 2023 and 2024 trees are near-duplicates at the top level; **2024 is the
newer and better-organised offering and should be the source of truth**, with
2023 consulted for the things 2024 dropped.

All of this material was written by **Professor Penny Kyburz**
(penny.kyburz@anu.edu.au), who convened the course in 2023 and 2024. Confirm
attribution and reuse with her before publishing any of it.

## What is in there

| Path (under `2024/`) | What | Size |
|---|---|---|
| `Theory/Week N - Complete/*.pptx` | 18 theory decks, the core lecture content | 200MB--1.2GB **each** |
| `Lectures/GameDev-Orientation-Lecture.pptx` | Week 1 orientation (54 slides) | 16MB |
| `Lectures/…-record-nopolls.pptx` | The same lecture with a screen recording embedded | 1.1GB |
| `Workshops/{Completed,Term 2}/*.pptx` | Workshop decks, weeks 2--12 | 0.2--1MB each |
| `Assessment/*.docx`, `Assessment/Individual/*.docx` | Assessment specs, templates and marking guides | ~3MB each |
| `Assessment/*.xlsx` | Peer assessment spreadsheets (student data — do not publish) | |
| `Awards/2023-Top5-*.docx` | Five award-winning 2023 student games | 100KB each |
| `GameDev-Learning-Outline.docx` | The week-by-week course structure | |
| `GameDev-Tutors.docx` | Tutor briefing (internal) | |
| `WW4-Photos/*.jpeg` | 40 photos of a week-4 workshop | ~2MB each |
| `ANU-Games.mp4` | Student game showreel (60MB) | |

`2023/` additionally has `Lectures/GameDev-Lecture-{1..7}.pptx` — the same
theory delivered as seven long decks (50--76 slides) before it was split into
the 2024 per-topic decks — and `Assessment/GameDev-Assessment-Labs.docx`, the
Game Labs assessment that 2024 dropped.

**Almost all of the 13GB is embedded video.** The 2024 theory decks are huge
because each has a dozen or more video clips embedded in the file; the text is
tiny. `GameDev-Theory-Week1-1-Play&Games.pptx` is 258MB for 12 slides, 69
images and 12 videos. Extracting the text from every `.pptx` and `.docx` in
the tree yields about 900KB of Markdown.

## Course shape (2024)

Lectures were recorded/asynchronous theory decks; the timetabled contact was
the weekly workshop. Theory ran weeks 1--5 and 7--9; workshops ran weeks 2--12.

| Week | Theory decks | Workshop |
|---|---|---|
| 1 | Play & Games; Formal Elements | (orientation lecture) |
| 2 | Playcentric Design Process; Idea Generation; Prototyping | Brainstorming, prototyping |
| 3 | Engaging the Player; Designing to Engage; Flow, Needs & Motivation | Game elements, prototyping |
| 4 | Systems; Mechanics; Balance | Mechanics, prototyping |
| 5 | Interface Design; Level Design | Interface design, prototyping |
| 6 | — | Level design, prototyping |
| 7 | Agile Game Development | Team formation, game project |
| 8 | Learning & Training; Challenge, Difficulty & Pacing | Playtesting, game project |
| 9 | Playtesting Process; Conducting Playtesting | game project |
| 10--12 | — | game project, peer marking |

Set texts: Fullerton, *Game Design Workshop*; Schell, *The Art of Game
Design*. Slides cite both by page throughout.

Tooling in 2024: **Unity** (students follow the Unity Junior Programmer
Pathway), **Unity Play** for WebGL builds, **Wattle** for submission, **MS
Forms** for peer assessment, **SONA** for research participation, and Poll
Everywhere for in-lecture polls. Note that none of this is GitLab — the
`templateRepo` front-matter field this site inherited from comp4350 may not
apply.

## Assessment (2024, totals 100%)

| Assessment | Components | Weight | Due (2024) |
|---|---|---|---|
| Game Prototype Progress | Prototype 4% + Progress report 8% | 12% | 5pm Mon 19 Aug |
| Game Proposal & Prototype | Prototype 10% + Proposal 21% | 31% | 5pm Mon 9 Sep |
| Developer Diary | Entry 1 8% + Entry 2 12% | 20% | 8 Oct, 30 Oct |
| Game Project (group) | Game 35%, coversheet 0%, peer assessment 0% | 35% | 5pm Mon 28 Oct |
| Research Participation & Reflection | — | 2% | 5pm Fri 8 Nov |

2023 differed: Game Labs 10% (weeks 2--6), Proposal 33%, five diary entries,
no Progress item.

Every assessment doc has a detailed rubric table, and there are separate
marking guides for the diary, progress and proposal. The rubrics convert
cleanly to Markdown tables.

## Conversion notes

`scripts/extract-ooxml.py` pulls the text out of every `.pptx` and `.docx`
without unpacking the media (it reads only the slide/document XML from the
zip, so the 1.2GB files cost nothing). Point it at the materials tree:

```sh
python3 scripts/extract-ooxml.py ../comp3540-materials /tmp/comp3540-text
```

Things the extracted text needs cleaned up:

- **Footer boilerplate on every slide.** `ANU SCHOOL OF COMPUTING   |   GAME
  DEVELOPMENT - WEEK N …`, the slide number, and a date like `22 JUL 24` land
  in the middle of each slide's text because they are shapes on the master.
  Strip them.
- **Reading citations** (`Fullerton p.102-103`) are separate shapes too, and
  are worth keeping — they become a citation line on the slide.
- **Speaker notes carry real content**, especially in the workshop decks
  (exercise references, background for the tutor). Decide per deck whether
  they belong on the page or in a `comment` fence.
- **Slide order is not reading order.** These are visually laid-out slides;
  the text comes out in shape order, which is roughly but not reliably
  top-to-bottom.
- **The media is the lecture.** A theory deck with 69 images and 12 videos
  does not survive as text. Any real conversion has to extract
  `ppt/media/*` and re-reference it, and decide what to do about the video
  (most of it is third-party clips that cannot be republished).
- **Poll Everywhere slides** are live-poll placeholders and should be dropped
  or replaced with a static prompt.
- **Student data must not be published**: the peer assessment `.xlsx` files,
  `GameDev-Tutors.docx`, and the `WW4-Photos` (people are identifiable
  without consent to publish).

## Suggested approach

1. **Assessments first.** The five `.docx` specs are self-contained, convert
   almost losslessly to Markdown, and are what students most need. This is
   the highest value for the least work.
2. **Workshops next.** The workshop decks are small, structured
   ("Before the workshop" / "In the workshop" / activities with timings) and
   map directly onto a content page per week — which suits the web better
   than a slide deck does.
3. **Theory last, and probably not as decks.** Either write new decks in
   `src/decks/` using the 2024 topic split as the outline, or publish the
   theory as content pages with the images extracted and the videos linked
   rather than embedded. A mechanical pptx→deck conversion would produce 18
   decks of stripped bullet points with the images missing, which is worse
   than either.

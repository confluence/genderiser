Genderiser
==========

What is this?
-------------

A program which assists writers in making the genders of characters within large bodies of English-language text dynamically configurable.

How does it do that?
--------------------

It replaces placeholder variables in the text with personal pronouns according to genders which can be configured for each character.

What is this for?
-----------------

I use this technique to write LARP character sheets.  It could potentially be used in other applications -- if you find it useful for something outside roleplaying games, let me know!

What's a LARP?
--------------

A Live Action RolePlaying game. I am most familiar with "theatre-style" LARPing involving once-off scenarios for 8-30 prewritten characters which run over the course of a single evening.  A LARP like this is essentially a distributed story: each character has a piece of the puzzle, and the plot happens when characters interact with each other.  What every character knows at the start of the LARP is contained within a personalized character sheet: a document which describes the background leading up to the event and the character's relationships with other characters.

Each player walks around during the LARP acting out their character, interacting with other characters and attempting to achieve their own goals.  It's like a play without a script and with the players as each other's audience. If you know tabletop roleplaying, it's like that, except with costumes and acting. If you know improv theatre, it's like improv theatre. If you hate improv theatre, it's nothing like improv theatre.

What does this have to do with gender?
--------------------------------------

There are many reasons to make some or all characters in a LARP gender-switchable, and to have a process for making these switches quickly at short notice:

* In my experience it is less commonplace for people to play cross-gender characters in LARPs than in tabletop games: in general people prefer to play characters which align with their real-life gender.. If all characters in a LARP have a fixed gender, this creates a rigid requirement for the gender split among the players in any given run, which may be difficult to satisfy and makes life difficult for the organiser. Sometimes there are too many interested players of a particular gender, and sometimes there are too few.  Gender-switchable characters allow the organiser to adjust the scenario to any player pool.

* Sometimes LARPs experience last-minute player drop-outs and replacements. This compounds the problem described above. An organiser can potentially replace a player with any other player irrespective of gender if that player is playing a gender-switchable character -- this makes last-minute replacements a lot less stressful.

* Personally I believe that in many cases writing characters in a more gender-neutral way leads to better-written, more interesting characters which rely less ongendered tropes and stereotypes. Your mieage may vary, and of course I understand that this approach may not work equally well in all fiction settings and genres.

While it is possible to change the gender of a character without making any alterations to the text, telling all the players to make a mental substitution as they play, this is not an ideal solution. It can break immersion and cause confusion. It's really nice to be able to hand out printed character sheets with all the names and pronouns seamlessly changed to reflect the actual state of the player pool.

Why is this hard?
-----------------

You might think that this is a trivial problem to solve: just print two character sheets for each gender-switchable character; one for "John Smith", and one for "Jane Smith"!  Unfortunately most of the changes required are not in the gender-switchable character's character sheet -- they're in all the other character sheets! Each character sheet is typically written in the second person, but refers to all the other characters in the third person. This is where the English language's gendered personal pronouns come into play.

If a 10-character LARP has a single gender-switchable character, and assuming that you are sticking to two gender possibilities, you could write two copies of the entire LARP: one in which the character is male and one in which she is female. You can do that by hand, although keeping both copies in sync would be pretty annoying. But what if there are two such characters? You have four possible combinations. Five characters? 32 combinations.  All ten?  1024.  Clearly this is no longer a tractable problem for non-technical LARP writers, although it is easy to solve with some kind of script if you are also a programmer.

I believe that this simple technical limitation is preventing writers who are not also programmers from making a particular creative choice in their writing, and I would like to change this by providing a simple, accessible program which non-technical users can integrate into their existing workflow.  I currently have a non-production-ready hacked-together prototype which I plan to replicate in a brand new, clean implementation.

Goals and milestones
--------------------

1. A basic implementation which runs on the command line, can process plain text files, handles masculine and feminine pronouns and obvious gendered words (e.g. "brother" / "sister") and allows the addition of custom additional gendered words. User documentation.

2. Integration with PmWiki, my CMS of choice. Preferably not via a complete reimplementation in PHP.

3. Integration with popular word processor file formats.

4. More pronoun options! Singular "they"; Spivak pronouns; possibility of adding custom gender options and word lists.

5. Fancy packaging and GUI

What about other (human) languages?
-----------------------------------

This is a (relatively) simple thing to do in English, because so few words actually need to change.  This idea is not necessarily portable to other languages -- in Polish, for example, all past-tense verbs are conjugated according to various properties which include the subject's gender.  You are welcome to fork this code and adapt it to your own language, but I have no plans to disappear down this particular rabbit hole any time soon.


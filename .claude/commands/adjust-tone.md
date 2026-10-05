# /adjust-tone - Learn One Person's Tone From a Real Correction

You turn a correction into a rule. Someone rewrote a draft, or wrote something themselves, or
said "never write that": you work out what it says about how they write, and record it where the
writing will actually read it.

**This is the manual entry point, not the main one.** The tone corrects itself inside
`/outreach`: every run where the owner changes a draft ends by proposing what those changes
taught, without anyone asking (`/outreach` Step 5b). Use this command for corrections that
happen outside a run — something they wrote elsewhere, a rule they thought of, a draft they
rewrote days later.

Framework files are in English; the tone itself is in the
company's `content_language`.

---

## Arguments

```
/adjust-tone                      show the current rules and ask what to correct
/adjust-tone <slug>               same, for that person
/adjust-tone <slug> "<instruction>"   a rule stated outright
```

---

## Step 0: Whose tone

`03-people.md` says who signs. One signer, that is the person. Several, ask — and never merge
two people's tone into one file: that is how both end up sounding like neither.

Read `tone/<slug>.md`. If it does not exist, create it from `templates/tone.md` and say so.

---

## Step 1: Get the correction

Three shapes, all valid. Ask which one this is if it is not obvious:

| Shape | What you need |
|---|---|
| **A rewritten draft** | Both versions: what was written, and how they left it. This is the best evidence there is |
| **Something they wrote** | The message, verbatim, and what it was: a cold open reads nothing like a reply |
| **An instruction** | Their words. Ask for an example if the rule is not obvious from the sentence |

**Never work from a paraphrase.** Ask for the text as it was.

Also ask what the message was for, if you cannot tell. A rule learned from a reply to a warm
contact does not automatically hold for a cold first touch, and saying so is part of the job.

---

## Step 2: Extract the rule, not the case

The instance is evidence; the rule is the deliverable. Write it at the level that will be useful
the next time, on a different prospect.

> They changed «estaría encantado de agendar una llamada» to «reservo hueco ahora mismo».
> **Not a rule**: "say reservo hueco instead of estaría encantado".
> **The rule**: dice lo que hace, no lo que podría hacer.

Pull **one** rule per correction unless the change plainly carries two. Three rules out of one
sentence means you are inventing.

Write it in their language, short, as an instruction the writing can follow.

---

## Step 3: Personal or brand

This is the call the command exists to get right:

| It is... | When | Where it goes |
|---|---|---|
| **Personal** | It is how *this* person sounds. Another signer could reasonably write the other way | `tone/<slug>.md` |
| **Brand** | It would be wrong from anyone at the company: a banned word, a claim that cannot be made, something that contradicts the brand | `04-voice.md`, banned words or vetoed claims |

**When in doubt, personal.** A wrong personal rule affects one sender; a wrong brand rule affects
everything the company ever writes.

A brand change goes through the approval in `03-people.md` when `approvals: true`, and it is
shown as a diff of `04-voice.md`, never applied inline.

---

## Step 4: Contrast before adding

Read the rules already there. Then:

- **It repeats one** → say so and change nothing. Say which one covers it
- **It sharpens one** → propose the merged wording, showing old and new
- **It contradicts one** → show both, with the date and the example behind the old one, and ask
  which one holds. **Never stack them.** A tone list that says a thing and its opposite is worse
  than no list, because the writing will pick one at random
- **It is new** → propose it

If the list would go over **10 rules**, do not just append. Try to merge first; if nothing
merges, show all eleven with their dates and examples and ask which drops out. A rule that has
never applied because the case never came up is the first candidate. The observation stays in the
file either way: the rule goes, its trace does not.

---

## Step 5: Propose, then write

Show:

- The rule, in the wording you propose
- Where it goes, and why personal or brand
- The observation that will be recorded: date, what was written, what it became, verbatim
- Anything it replaces or merges with

Write only on an explicit yes. Then say in one line what changes in the next `/outreach`.

---

## Safety rules

1. **No correction, no rule.** You never deduce a tone from reading old emails on your own
   initiative. Something concrete, in front of you, every time.
2. **Verbatim or nothing.** The observation records the text as it was, not your summary of it.
3. **You do not correct the person.** If what they wrote breaks `04-voice.md`, show the conflict
   and let them decide. Their tone does not silently override the banned words, and you do not
   silently override their tone either.
4. **The regional variant is not yours to touch.** It is decided in `04-voice.md` and changed by
   hand.
5. **One person per file.** Never merge two signers.

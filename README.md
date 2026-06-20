# LinkedIn Post Harness

A Claude Code skill that writes and publishes LinkedIn posts using a **Planner → Generator → Evaluator** harness, directly adapted from Anthropic's [Harness Design for Long-Running Application Development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (Prithvi Rajasekaran, 2026).

## Why a Harness for LinkedIn Posts?

Single-pass AI writing produces generic, cliche-heavy posts. This skill separates **drafting** from **judging** (the GAN-inspired core idea from Anthropic's article) and iterates through rubric-graded rounds until quality thresholds are met — the same architecture that produced "creative leaps" in Anthropic's frontend design experiments.

## How It Works

```
You: "Write a LinkedIn post about X"
         |
    [Planner] ─── spec.md + sprint contract ──→ You approve
         |
    [Generator] ── post_v1.md + handoff.md
         |
    [Evaluator] ── critique.md (4 criteria, each 1-5)
         |          fail → Generator revises (up to 3x)
         |          pass → next round
         |
     ... R1 → R2 → R3 ...
         |
    final_post.md confirmed
         |
    ★ You review full post → explicit approval required ★
         |
    Published via LinkedIn API
```

## Key Principles (from the article)

| Article Concept | LinkedIn Mapping |
|---|---|
| GAN-style generator/evaluator split | Draft-writer and critic are strictly separated roles |
| Context anxiety | Never close a draft early because it "looks long enough" — only rubric pass ends a round |
| Context resets + structured handoff | `handoff.md` at each round boundary; next round starts fresh |
| Sprint contract negotiation | Planner and Generator agree on "done" criteria before any drafting |
| Self-evaluation bias | Generator **never** self-grades — only the Evaluator scores |
| Strategic pivot | If scores stagnate, Generator pivots perspective/tone/structure entirely |
| Evaluator self-convincing guard | Detects the pattern: "finds issue → talks itself into ignoring it" |
| Simplest solution first | Simple announcements collapse to a single-pass; thought leadership gets multi-round |
| V1→V2 evolution | Sprints removed for capable models, but Planner + Evaluator always kept |

Full article inventory preserved in [`references/source-article-inventory.md`](references/source-article-inventory.md).

## Grading Criteria (each 1-5, pass = all >= 4)

1. **Strategic coherence** — Hook → claim → evidence → CTA read as one cohesive unit
2. **Originality & insight** — Non-obvious perspective unique to this topic; penalizes cliches and AI slop
3. **Craft** — Sentence density, rhythm, formatting, tone consistency, typos
4. **Action clarity** — Reader knows exactly what to do next (save, comment, DM, click)

**Weighting:** Strategic coherence and Originality rank above Craft and Action clarity (matching the article's emphasis on design quality and originality).

## Setup

### 1. Environment Variables

```bash
# Add to ~/.zshrc or ~/.bashrc
export LINKEDIN_ACCESS_TOKEN="your-oauth2-access-token"
export LINKEDIN_AUTHOR_URN="urn:li:person:your-member-id"
# For company pages:
# export LINKEDIN_AUTHOR_URN="urn:li:organization:your-org-id"
```

### 2. Get a LinkedIn Access Token

1. Create an app at [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Add **Share on LinkedIn** (or **Marketing Developer Platform**) product
3. Complete OAuth 2.0 Authorization Code Flow with `w_member_social` scope
4. Call `/v2/userinfo` to get your member ID for the URN

### 3. Install

Copy the `linkedin-post-harness/` folder into `~/.claude/skills/`.

## Usage

### Trigger Phrases

Just say any of these in Claude Code:

- "Write a LinkedIn post about..."
- "Post to LinkedIn about..."
- "LinkedIn thought leadership on..."

### Publish Script

```bash
# Text post
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md

# With link preview
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md \
  --link "https://example.com" --link-title "Title"

# With image upload
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md \
  --image ./cover.png --image-alt "Description"

# Dry run (preview payload only)
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md --dry-run
```

The script requires typing `"yes"` to confirm by default. Pass `--yes` to skip if approval was already given in chat.

### Script Options

| Option | Description | Required |
|---|---|---|
| `--text` / `--text-file` | Post body (inline or file path) | Yes (one of) |
| `--visibility` | `PUBLIC` (default) or `CONNECTIONS` | No |
| `--link` | Article URL for link preview | No |
| `--link-title` | Preview title | No |
| `--link-description` | Preview description | No |
| `--image` | Local image path to upload | No |
| `--image-alt` | Alt text for image | No |
| `--dry-run` | Print payload without posting | No |
| `--yes` | Skip interactive confirmation | No |

## Output Files

All artifacts are written to a `linkedin-post/` directory:

| File | Contents |
|---|---|
| `spec.md` | Planner's spec and sprint contracts |
| `post_v1.md` ... `post_vN.md` | Drafts per round |
| `critique_v1.md` ... | Evaluator scores and feedback |
| `handoff.md` | Round-to-round handoff notes |
| `final_post.md` | Approved final post |
| `publish_log.md` | Post URN, timestamp, author (after publish) |

## Safety

- **Mandatory human gate**: The skill will never publish without your explicit approval, even after all evaluation rounds pass
- **Interactive confirmation**: The publish script prompts for `"yes"` before calling the API
- **Dry run**: Always available via `--dry-run` to inspect the payload
- **3,000 char limit**: Enforced by both the evaluator and the script

## Project Structure

```
linkedin-post-harness/
├── SKILL.md                              # Harness instructions
├── README.md                             # This file
├── README.ko.md                          # Korean README
├── scripts/
│   └── publish_linkedin.py               # LinkedIn UGC Posts API publisher
└── references/
    ├── source-article-inventory.md       # Full article inventory (preserved)
    ├── post-patterns.md                  # Hook patterns, templates, AI slop checklist
    └── linkedin-api.md                   # API notes and rate limits
```

## Credits

Methodology adapted from:
- **"Harness Design for Long-Running Application Development"** by Prithvi Rajasekaran, Anthropic (Mar 2026)
- Applies the Planner → Generator → Evaluator three-agent architecture, sprint contracts, context resets, rubric-based evaluation, and self-evaluation bias safeguards to the LinkedIn post writing domain.

## License

MIT

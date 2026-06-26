# A/V & Room Checklist

Use this checklist when setting up for an in-person or virtual delivery.

---

## In-Person Delivery

### Room — Day before

- [ ] Confirm room capacity (recommend ≤ 20 people for a hands-on lab format)
- [ ] Confirm tables allow attendees to work on laptops (not theatre-style seating)
- [ ] Test the projector/display: confirm it accepts HDMI or USB-C from your laptop
- [ ] Confirm there is a whiteboard or flip chart (used for agent loop diagrams)
- [ ] Confirm the room WiFi supports simultaneous `docker pull` for 20 devices
      (dev container image is ~3 GB — this is the single biggest bandwidth requirement)
- [ ] Arrange for a power strip at each table (laptops + potentially monitors)

### Room — Morning of delivery

- [ ] Arrive 30 minutes early
- [ ] Connect your laptop to the projector — confirm slides display correctly at 16:9
- [ ] Open the slide deck (`slides/zava-microhack-deck.md` built to HTML, or use Marp in VS Code)
- [ ] Open a terminal with the dev container running and the API responding to `curl`
- [ ] Write the repo URL on the whiteboard: `https://github.com/NikoMix/microhack-ai-apps`
- [ ] Write the WiFi password on the whiteboard
- [ ] Set up a second monitor or terminal window with the solution branches ready

### A/V

- [ ] Laptop → projector cable / adapter (HDMI, USB-C, or DisplayPort — bring all adapters)
- [ ] If using a lavalier mic, test audio level with a 30-second recording
- [ ] Confirm room speakers are working if you'll play any audio
- [ ] Presenter remote / clicker for slide navigation (optional but recommended)
- [ ] Screen mirroring to a secondary display for attendees at the back of the room

### Food & breaks

- [ ] Confirm coffee/tea is available at 08:15 (before the session starts)
- [ ] Lunch at 12:00 — book for the full group or confirm a nearby option
- [ ] Afternoon break snacks at 15:00

---

## Virtual Delivery (Teams / Zoom)

### Before the session

- [ ] Create the meeting with a lobby — admit attendees manually to avoid join disruption
- [ ] Share the repo URL and prerequisites list in the meeting invite
- [ ] Prepare screen-share of the terminal with the dev container running
- [ ] Test screen sharing at full resolution (slides + code must be legible)
- [ ] Confirm you can share a specific window (not full screen) for security
- [ ] Set up a second virtual desktop with the solution branches ready

### During the session

- [ ] Share slides as a window, not full-screen (allows quick alt-tab to terminal)
- [ ] Use a virtual whiteboard (Miro, Microsoft Whiteboard) for the agent loop diagram
  - Prepare a basic agent loop template in advance
- [ ] Have "Raise Hand" enabled for Q&A
- [ ] Use breakout rooms during labs so attendees can ask questions in small groups
  - Create one breakout room per 4–5 attendees
  - Assign a helper (co-facilitator or experienced attendee) per room
- [ ] Record the session for attendees who want to re-watch (confirm consent)

### Virtual A/V checks (30 min before)

- [ ] Camera angle — attendees should see your face and your screen simultaneously
- [ ] Audio — no echo, no background noise; use a headset or quality mic
- [ ] Internet — wired connection preferred; test upload speed > 5 Mbps
- [ ] Background — virtual background or clean, professional environment
- [ ] `curl` test to GitHub Models from the terminal you'll share

---

## Hybrid Delivery (In-person + Remote)

Hybrid is the most complex mode. Additional requirements:

- [ ] Camera covering in-room whiteboard and presenter
- [ ] Confidence monitor or secondary display showing the remote participants
- [ ] Dedicated chat moderator for remote participants
- [ ] Test audio — remote participants must be able to hear room questions clearly
- [ ] Test whiteboard camera — remote participants should be able to read the whiteboard

---

## Slide deck setup

The slide deck builds to HTML and PDF via the `slides.yml` GitHub Actions workflow.

### To display slides locally during delivery

**Option 1 — HTML in browser (recommended):**

```bash
# Build HTML locally
npx @marp-team/marp-cli@latest slides/zava-microhack-deck.md \
  -o /tmp/zava-deck.html --html
# Open in browser
open /tmp/zava-deck.html   # macOS
# or: start /tmp/zava-deck.html   # Windows
```

Navigate with arrow keys. Press `F` for fullscreen, `P` for presenter view.

**Option 2 — Marp VS Code extension:**

Install the [Marp for VS Code extension](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode). Open `slides/zava-microhack-deck.md` → click the Marp preview icon → `Marp: Open Preview to the Side`.

**Option 3 — PDF:**

```bash
npx @marp-team/marp-cli@latest slides/zava-microhack-deck.md \
  -o /tmp/zava-deck.pdf --pdf --allow-local-files
```

Open in your preferred PDF viewer and use fullscreen presentation mode.

---

## Pre-session sanity checks

Run these checks 30 minutes before the session starts:

```bash
# 1. Dev container is running
docker ps | grep microhack

# 2. GitHub Models responds
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://models.github.ai/inference/models | head -c 100

# 3. API starts cleanly
cd src/python && make run &
sleep 5 && curl http://localhost:8000/health

# 4. Slides build
npx @marp-team/marp-cli@latest slides/zava-microhack-deck.md \
  -o /tmp/test.html --html && echo "Slides OK"
```

All four checks must pass before the session starts.

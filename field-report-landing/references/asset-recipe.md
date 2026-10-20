# Asset recipe: still, clip, frames (Magnific)

How the hero orbit and the push-in were made, with the prompts that worked, why each step exists, and what went wrong. Tool names are the Magnific MCP's (`images_generate`, `video_generate`, `simulate_cost`); the same pattern works with any image-to-video tool that accepts a start frame.

## Contents
- Principles
- Step 1: the still
- Step 2: the clip
- Step 3: frames
- Optional: a push-in and a map still
- Provenance
- What went wrong

## Principles

- **Still first.** A still costs about 75 credits; a clip costs thousands. Settle composition and style on stills, then animate only the winner. Why: iteration is cheap on images and expensive on video.
- **The still is the start frame.** Seedance-class models accept a start frame OR reference images, not both. Passing the approved still as `keyframes.start` keeps the clip faithful to it.
- **No text in generated media.** Generated text garbles. Write labels and numbers as real DOM text on top. Every prompt says "no text, no labels".
- **Style by reference, not by name.** Upload two reference images and pass them as `references: [{type: "style", ...}]` for the still. They set style only. Start from the bundled frames in `assets/style-reference/` (the owner's own earlier hero, see its README): they carry the house line weight, grey and framing, so the new page matches the old ones. Do not ship or imitate a company's artwork. Once you have one good still for the new project, use it as an extra reference for later stills so that set stays consistent.
- **Ask before spending.** Run `simulate_cost` for each generation and tell the user the total.

## Step 1: the still

Prompt shape (fill the angle brackets with the project's own layers):

```
Isometric exploded view of <N> stacked horizontal layers floating apart on a near-black
background, thin crisp white line art, wireframe slabs. From bottom to top: <layer 1>,
<layer 2>, ... <top layer>. A curved pale arrow rises along the left side from the bottom
layer to the top. No text, no labels, no people. Match the reference style exactly:
monochrome, hairline strokes, matte black, engineering-diagram feel.
```
Settings that worked: `aspectRatio: "16:9"`, `count: 4` variants, `references` of type `style` (two). Pick the variant with clear separation between layers and room around the stack.

Variant for a scene that must sit far away (used before a push-in): "seen from slightly above and far away ... lots of empty dark margin around the stack, hairline pale-blue and white linework". The margin matters: the camera needs space to move.

## Step 2: the clip

Model: `bytedance-seedance-pro-2.5`, 16:9, 1080p, `keyframes.start` = the chosen still, `noMusic: true`, no sound effects.

Orbit prompt that worked (10 s):
```
Locked-off technical animation of the same isometric exploded stack of <N> wireframe layers
on matte near-black. The layers start separated; over ten seconds the camera glides smoothly
in a slow orbit to the left, rotating about 50 degrees while descending slightly, so the stack
is seen from a lower, more dramatic angle and then from above, keeping perspective consistent.
Layers stay perfectly rigid and parallel, hairline white strokes stay crisp, the curved arrow
stays attached. Pale blue light pulses travel up from the bottom layer through each layer to
the top layer along the lines. No new objects, no text, no morphing, no flicker, no people,
no color other than white, grey and faint blue.
```
Push-in prompt (8 s) that worked:
```
Slow continuous push-in. The camera glides forward and rises over the layers, tilting down,
until the top plane fills the whole frame. The layers stay rigid and parallel, nothing deforms.
Pale blue pulses travel up the curved arrow into the top plane. No new objects, no text, no cuts.
```
Reuse the phrases "layers rigid and parallel", "no new objects, no text", "nothing deforms": they are what keeps the model from inventing geometry. Use `Draft` resolution first when the tool offers it (cheap check of motion), then finalise the winner at 1080p within the draft's deadline.

## Step 3: frames

`scripts/frames_from_clip.sh` does the mechanical part: every Nth frame, optional crop, scale, grade, WebP. The first build used every 3rd frame, a 1000x1080 centre crop of the 1920x1080 clip (`--crop 1000:1080:460:0`, so the stack fills a portrait stage), scaled to 800 wide, saturation 0.7, black point lifted, quality 62. The script defaults to no crop, so pass `--crop` when your stage is not 16:9. Example: `frames_from_clip.sh clip.mp4 public/landing/orbit --crop 1000:1080:460:0`. A 10 s clip at 24 fps gives 81 frames; an 8 s push gives 65. The exact grading values of the first build were not recorded; the script's defaults are a starting point, so check the first frames against the hero and adjust `--sat` and `--black`.

On the page, draw frames to a `<canvas>` with `mix-blend-mode: screen`. The sticky parent must carry its own ground colour, or the blend shows through to whatever is behind.

## Optional: a spatial still

For a map or night-view still used as a background: generate (auto model, 2:1), then `images_upscale` 2x (creative, subtle). Prompt used: "night satellite view of <region> from low orbit, city lights, faint shipping lanes as thin luminous lines across dark water, cloud wisps, near-black and deep steel-blue tones, documentary realism, no text". Label it on the page as a generated image, not a photograph.

## Provenance

Every shipped raster gets a sidecar (generation tool, model, prompt, date) and an entry in `PROVENANCE.md`. Keep sidecars out of the served folder (for example `asset-sources/` that is also in `.dockerignore`). Say on the page which images are generated art. Why: it is both honest and the first thing a technical reviewer checks.

## What went wrong

- **Bloom and halos** appeared around bright nodes and an arrow tip, in conflict with "no glow". Fix in grading: lift the black point and reduce saturation; re-check the arrow tip specifically.
- **The signal blue washed out** after desaturating, so the orbit lost the page's one accent. After grading, confirm the blue is still readable, or grade selectively.
- **Hero SVG and orbit frames disagreed** (a layer drawn as a bar list in one and a cell grid in the other; different line weight and grey). Redraw the SVG to match the generated frames.
- **Camera barely moved** between the first and last caption. If captions are anchored to layers, the orbit must sweep enough to show different layers; raise the rotation in the prompt.

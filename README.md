# Sky & Atmospheric Phenomena Analyzer

## Context

Build a small full-stack application that analyzes an image and returns **Sky & Atmospheric Phenomena** tags using a YOLO-based computer vision approach.

You will implement:

- a backend service (Python or Go)
- a REST API that you design and document
- a React UI that uploads an image and displays results

AI coding tools are allowed.

---

## What we are building

### Computer Vision (YOLO)

Use a YOLO library to produce predictions from an image.

You may choose one approach:

- **Inference-first:** use an existing YOLO model and map outputs to the taxonomy below
- **Mini fine-tune (optional):** fine-tune a small YOLO model on the provided dataset

Accuracy is not the main focus. Reasoning and engineering decisions matter more.

---

## Taxonomy

All predictions must map into:

**Group label:** `atmosphere`

Required labels:
- clear_sky
- clouds
- sunset_sunrise
- night_sky_stars
- fog_mist_haze
- rainbow_lightning

You may introduce additional sublabels, but the labels above must be supported.

---

## Frontend (React)

A minimal React + Vite project is provided.
To get the client running:

```bash
cd client
npm install        # or yarn
npm run dev         # start Vite development server
```
Expected functionality:
- image upload UI
- results view (tags + confidence)
- loading and error states
- optional annotated preview

Styling is not the focus.

---

## Backend

Implement a backend service that:

- accepts an image upload
- runs a CV pipeline
- returns a JSON response of your design
- documents API and architecture decisions in the README

Guidelines:

- REST API
- clear project structure
- reasonable validation and error handling
- explain how you would productionize it

Constraints:

- No authentication required
- Persistence is optional

### Backend guidance

You may pick **Python or Go**; a simple `server/README.md` should include the commands needed to bootstrap and start the service. A conventional layout looks like:

```
server/
  app.py            # or main.go
  requirements.txt  # or go.mod/go.sum
  handlers/         # request handlers/controllers
  models/           # any training/inference code
  utils/            # shared helpers
```


---

## Dataset

A small YOLO-format dataset is included under:

`assets/dataset/`

*Image source:* the training images were taken from the SkyFinder dataset: https://cs.valdosta.edu/~rpmihail/skyfinder/

You may use it for fine-tuning, experimentation, or ignore it if you prefer an inference-first approach.

---

## Deliverables

Update this repository with:

- your implementation
- documentation explaining:
  - how to run
  - your API design
  - architecture overview
  - CV approach
  - limitations and next steps

---

## Notes

If something is unclear, make a reasonable assumption and document it.

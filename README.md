# Smart SMS AI Backend

FastAPI backend for the personal Smart SMS Assistant Android app.

## Environment variable

Set `GEMINI_API_KEY` in your hosting provider. Never commit the key to GitHub.

Optional:

`GEMINI_MODEL=gemini-2.5-flash`

## Endpoints

- `GET /` service status
- `GET /health` configuration status
- `POST /generate` returns three SMS reply suggestions

## Render

This repository includes `render.yaml`. Create a Render Blueprint from this repository and enter `GEMINI_API_KEY` when Render requests it.

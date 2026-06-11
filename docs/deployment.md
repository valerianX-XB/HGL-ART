# Deployment

## Local setup

```bash
npm install
npm run prepare:data
npm run dev
```

## Build

```bash
npm run validate:data
npm run build
npm run preview
```

## GitHub repo creation

```bash
git init
git add .
git commit -m "Initial HGL ART 3D market map"
gh repo create hgl-art-3d-market-map --public --source=. --remote=origin --push
```

## GitHub Pages

The included workflow `.github/workflows/deploy.yml` builds the Vite app and deploys `dist/` to GitHub Pages.

In GitHub:
1. Open repository Settings.
2. Go to Pages.
3. Select GitHub Actions as the source.
4. Push to `main`.

## Map tokens

This project uses MapLibre GL with a public Carto basemap and does not require a Mapbox token.

## Updating data later

1. Update the corrected research package.
2. Run `npm run prepare:data` with the correct source path if needed.
3. Run `npm run validate:data`.
4. Commit updated `public/data` files.

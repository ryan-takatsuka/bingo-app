# Image Duplication Analysis

## Current Situation

Images are currently duplicated in two locations:
- `/bingo_v2/images/` - Used by the Flask backend
- `/bingo_v2/frontend/public/images/` - Potentially redundant

## Investigation Results

1. The Flask backend serves images from `/bingo_v2/images/` directory
2. The React frontend fetches images via the Flask API (e.g., `/api/images/background`)
3. All image loading in the React app appears to use the Flask API, not static files from public/images

## Recommendation

The `/bingo_v2/frontend/public/images/` directory is unnecessary and should be removed because:
1. It duplicates the backend images, increasing repository size
2. The frontend doesn't actually serve these images directly - it uses the Flask API
3. This creates confusion about where images should be updated

## Actions to Take

1. Remove the `/bingo_v2/frontend/public/images/` directory
2. Ensure all image management is done through the Flask backend
3. Update any documentation to clarify that images should only be placed in `/bingo_v2/images/`

## File Sizes

Total duplicate size: ~2.5MB
- default_background.png: 1,671,304 bytes
- hexy_bald.png: 453,637 bytes
- hexydobby.jpg: 48,651 bytes
- rat_king.png: 276,005 bytes

Removing these duplicates will save ~2.5MB from the repository.
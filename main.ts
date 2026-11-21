// news-image-20261120 entry (Node 22, standard library only): the image is the
// entry.png beside this file, drawn by draw.py from stories.json, and this program
// copies it to /output/entry.png. Run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(
  new URL('./entry.png', import.meta.url),
  join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'),
);

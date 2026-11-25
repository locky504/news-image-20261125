// news-image-20261125 entrypoint (Node 22, standard library only).
// Copies the pre-rendered front page entry.png beside this file to
// /output/entry.png, validates its PNG magic bytes, and prints its sha256.
// No network at run time; two runs write identical bytes.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { createHash } from 'node:crypto';
import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576; // the gate's 1 MiB cap

const src = new URL('./entry.png', import.meta.url);
const data = readFileSync(src);

if (data.length < 8 || !data.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error('entry.png is not a PNG: bad magic bytes');
}
if (data.length > MAX_BYTES) {
  throw new Error(`entry.png is ${data.length} bytes, over the 1 MiB cap`);
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const out = join(outDir, 'entry.png');
copyFileSync(src, out);

const digest = createHash('sha256').update(data).digest('hex');
console.log(`entry.png sha256 ${digest} (${data.length} bytes)`);

import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const code = (await readFile(new URL('../wix/syncGifViews.jsw', import.meta.url), 'utf8'))
  .replace(/^import .*;$/gm, '').replace('export async function', 'async function');
const baseline = { _id: 'known-item', key: 'gifViews', display: '7.3M', rawViews: 7300000, updatedAt: new Date(Date.now() - 3600000) };
const valid = { schemaVersion: 1, channel: 'coineasy', source: 'https://giphy.com/coineasy', display: '7.4M', approximateViews: 7400000, precision: 'giphy-public-rounded-display', checkedAt: new Date().toISOString() };
async function run(feed, { status = 200, existing = baseline } = {}) {
  let writes = 0;
  let stored = { ...existing };
  const query = { eq() { return this; }, limit() { return this; }, async find() { return { items: [stored] }; } };
  const context = vm.createContext({
    console,
    fetch: async () => ({ status, text: async () => JSON.stringify(feed) }),
    wixData: {
      query: () => query,
      update: async (collection, item) => { writes++; stored = item; return item; },
      get: async () => stored,
    },
  });
  vm.runInContext(code, context);
  try { return { result: await context.syncGifViews(), writes }; }
  catch (error) { return { error, writes }; }
}
const success = await run(valid);
assert.equal(success.result.status, 'updated');
assert.equal(success.writes, 1);
for (const feed of [
  { ...valid, channel: 'wrong' },
  { ...valid, checkedAt: new Date(Date.now() - 72 * 3600000).toISOString() },
  { ...valid, checkedAt: new Date(Date.now() + 3600000).toISOString() },
  { ...valid, approximateViews: 999 },
  { ...valid, display: '7.4M injected' },
  { ...valid, display: '7M', approximateViews: 7000000 },
]) {
  const result = await run(feed);
  assert.ok(result.error);
  assert.equal(result.writes, 0);
}
const failedHttp = await run(valid, { status: 403 });
assert.ok(failedHttp.error);
assert.equal(failedHttp.writes, 0);
const duplicate = await run(valid, { existing: { ...baseline, updatedAt: valid.checkedAt } });
assert.equal(duplicate.result.status, 'unchanged');
assert.equal(duplicate.writes, 0);
console.log('Wix import: success, stale/future/source/count/decrease/HTTP guards and deduplication passed');

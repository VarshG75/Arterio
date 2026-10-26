/* Route memory runs without a browser; Chrome checks cover the visible reveal. */
const test = require('node:test');
const assert = require('node:assert/strict');
const {createPageMemory} = require('../app_and_ml/assets/brand/navigation.js');

test('new pages start at the top and remember their own positions', () => {
  const memory = createPageMemory();
  assert.equal(memory.enter('clinical-docs'), 0);
  memory.restored();
  memory.remember(780);
  assert.equal(memory.begin('architecture', 810), true);
  memory.remember(0); // The outgoing DOM may shrink during navigation.
  assert.equal(memory.enter('architecture'), 0);
  memory.restored();
  memory.remember(420);
  memory.begin('clinical-docs', 420);
  assert.equal(memory.enter('clinical-docs'), 810);
  memory.restored();
  memory.begin('architecture', 810);
  assert.equal(memory.enter('architecture'), 420);
});

test('widget updates and repeated events do not restart a page entrance', () => {
  const memory = createPageMemory();
  memory.enter('telemetry');
  memory.restored();
  memory.remember(250);
  assert.equal(memory.begin('telemetry', 250), false);
  assert.equal(memory.enter('telemetry'), null);
  assert.equal(memory.begin('heart-explorer', 250), true);
  assert.equal(memory.begin('heart-explorer', 0), false);
  assert.equal(memory.enter('heart-explorer'), 0);
});

test('rapid page changes preserve the outgoing position', () => {
  const memory = createPageMemory();
  memory.enter('clinical-docs');
  memory.restored();
  memory.begin('architecture', 640);
  memory.begin('heart-explorer', 0);
  memory.enter('heart-explorer');
  memory.restored();
  memory.begin('clinical-docs', 90);
  assert.equal(memory.enter('clinical-docs'), 640);
});

test('a new document replays the current page from the top', () => {
  const previous = createPageMemory();
  previous.enter('heart-explorer');
  previous.restored();
  previous.remember(900);
  const refreshed = createPageMemory();
  assert.equal(refreshed.enter('heart-explorer'), 0);
});

test('temporary restoration clamping does not overwrite a saved position', () => {
  const memory = createPageMemory();
  memory.enter('heart-explorer');
  memory.restored();
  memory.begin('cohort', 950);
  memory.enter('cohort');
  memory.restored();
  memory.begin('heart-explorer', 100);
  assert.equal(memory.enter('heart-explorer'), 950);
  memory.remember(0);
  memory.begin('cohort', 0);
  memory.enter('cohort');
  memory.restored();
  memory.begin('heart-explorer', 100);
  assert.equal(memory.enter('heart-explorer'), 950);
});

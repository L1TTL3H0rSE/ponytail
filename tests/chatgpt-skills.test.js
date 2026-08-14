#!/usr/bin/env node

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.join(__dirname, '..');
const builder = path.join(root, 'scripts', 'build-chatgpt-skills.py');
const skills = [
  'ponytail',
  'ponytail-review',
  'ponytail-audit',
  'ponytail-debt',
  'ponytail-gain',
  'ponytail-help',
];

function pythonCommand() {
  for (const command of ['python3', 'python']) {
    const result = spawnSync(command, ['--version'], { encoding: 'utf8' });
    if (result.status === 0) return command;
  }
  return null;
}

test('ChatGPT skill packager strips host-only frontmatter and adds UI metadata', (t) => {
  const python = pythonCommand();
  if (!python) {
    t.skip('python is required for the ChatGPT skill packager');
    return;
  }

  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'ponytail-chatgpt-'));
  const output = path.join(fixture, 'out');
  t.after(() => fs.rmSync(fixture, { recursive: true, force: true }));

  for (const skill of skills) {
    const dir = path.join(fixture, 'skills', skill);
    fs.mkdirSync(path.join(dir, 'references'), { recursive: true });
    fs.writeFileSync(
      path.join(dir, 'SKILL.md'),
      `---\nname: ${skill}\ndescription: >\n  Test description for ${skill}.\nargument-hint: "[test]"\nlicense: MIT\n---\n\n# Test\n`,
    );
    fs.writeFileSync(path.join(dir, 'references', 'keep.txt'), 'kept\n');
  }

  const result = spawnSync(
    python,
    [builder, '--root', fixture, '--output', output],
    { encoding: 'utf8' },
  );
  assert.equal(result.status, 0, result.stderr || result.stdout);

  for (const skill of skills) {
    const archive = path.join(output, skill, 'skill.zip');
    assert.ok(fs.existsSync(archive), `${skill} archive should exist`);

    const check = spawnSync(
      python,
      ['-c', [
        'import sys, zipfile',
        'z=zipfile.ZipFile(sys.argv[1])',
        'skill=sys.argv[2]',
        'md=z.read(f"{skill}/SKILL.md").decode()',
        'assert "argument-hint:" not in md',
        'assert "license:" not in md',
        'assert f"{skill}/agents/openai.yaml" in z.namelist()',
        'assert f"{skill}/references/keep.txt" in z.namelist()',
      ].join(';'), archive, skill],
      { encoding: 'utf8' },
    );
    assert.equal(check.status, 0, check.stderr || check.stdout);
  }
});

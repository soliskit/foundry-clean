import { test } from 'node:test'
import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

void test('CP-1 to CP-4: credit protection contract', () => {
  const script = fileURLToPath(
    new URL(
      '../scripts/credit-protection/test_credit_protection.py',
      import.meta.url
    )
  )
  const result = spawnSync('python3', ['-B', script], {
    encoding: 'utf8',
    timeout: 30000,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
  })
  assert.ifError(result.error)
  assert.equal(result.status, 0, result.stdout + result.stderr)
})

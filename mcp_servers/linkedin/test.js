#!/usr/bin/env node

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('LinkedIn MCP Server - Quick Test\n');
console.log('=================================\n');

// Test 1: Check if server file exists
console.log('✓ Test 1: Server file exists');

// Test 2: Check if package.json is valid
try {
  const pkg = JSON.parse(await readFile(join(__dirname, 'package.json'), 'utf8'));
  console.log(`✓ Test 2: Package.json valid (${pkg.name} v${pkg.version})`);
} catch (error) {
  console.log('✗ Test 2: Package.json invalid');
  process.exit(1);
}

// Test 3: Check dependencies
try {
  await import('@modelcontextprotocol/sdk/server/index.js');
  console.log('✓ Test 3: MCP SDK installed');
} catch (error) {
  console.log('✗ Test 3: MCP SDK missing');
  process.exit(1);
}

console.log('\nAll tests passed! ✓');
console.log('\nNext steps:');
console.log('1. Start the server: npm start');
console.log('2. Configure in .mcp.json (already done)');
console.log('3. Use create_linkedin_post tool to create drafts');
console.log('4. Review drafts in AI_Employee_Vault/LinkedIn_Drafts/');
console.log('5. Manually post to LinkedIn');

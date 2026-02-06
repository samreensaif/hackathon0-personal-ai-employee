#!/usr/bin/env node

/**
 * OAuth2 Authorization Helper for Gmail MCP Server
 *
 * This script helps you obtain OAuth2 tokens for the Gmail API.
 * Run this once to authorize the application and generate token.json.
 */

import { google } from 'googleapis';
import { promises as fs } from 'fs';
import readline from 'readline';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CONFIG_PATH = path.join(__dirname, 'config.json');
const TOKEN_PATH = path.join(__dirname, 'token.json');

// Gmail API scopes required
const SCOPES = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.compose',
  'https://www.googleapis.com/auth/gmail.readonly',
  'https://www.googleapis.com/auth/gmail.modify'
];

/**
 * Load credentials from config.json
 */
async function loadCredentials() {
  try {
    const content = await fs.readFile(CONFIG_PATH, 'utf8');
    const config = JSON.parse(content);

    if (!config.installed && !config.web) {
      throw new Error('Invalid config.json format. Expected "installed" or "web" credentials.');
    }

    return config.installed || config.web;
  } catch (error) {
    console.error('Error loading config.json:', error.message);
    console.error('\nPlease ensure config.json exists and contains valid OAuth2 credentials.');
    console.error('See README.md for setup instructions.');
    process.exit(1);
  }
}

/**
 * Run the OAuth2 authorization flow
 */
async function authorize() {
  console.log('Gmail MCP Server - OAuth2 Authorization\n');

  const credentials = await loadCredentials();
  const { client_id, client_secret, redirect_uris } = credentials;

  const oauth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    redirect_uris[0]
  );

  // Generate authorization URL
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent' // Force consent screen to get refresh token
  });

  console.log('Step 1: Authorize this application by visiting this URL:');
  console.log('\n' + authUrl + '\n');
  console.log('Step 2: After authorization, you will receive a code.');
  console.log('Step 3: Copy that code and paste it below.\n');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve, reject) => {
    rl.question('Enter the authorization code: ', async (code) => {
      rl.close();

      try {
        // Exchange authorization code for tokens
        const { tokens } = await oauth2Client.getToken(code);

        // Save tokens to file
        await fs.writeFile(TOKEN_PATH, JSON.stringify(tokens, null, 2));

        console.log('\n✓ Success! Token has been saved to token.json');
        console.log('✓ You can now run the Gmail MCP Server with: node server.js');
        console.log('\nToken details:');
        console.log(`  Access Token: ${tokens.access_token ? '✓ Present' : '✗ Missing'}`);
        console.log(`  Refresh Token: ${tokens.refresh_token ? '✓ Present' : '✗ Missing'}`);
        console.log(`  Expires: ${tokens.expiry_date ? new Date(tokens.expiry_date).toLocaleString() : 'N/A'}`);

        if (!tokens.refresh_token) {
          console.warn('\n⚠ Warning: No refresh token received. You may need to revoke access and re-authorize.');
          console.warn('   Visit: https://myaccount.google.com/permissions');
        }

        resolve();
      } catch (error) {
        console.error('\n✗ Error exchanging authorization code:', error.message);
        console.error('\nPlease try again and make sure you copied the entire code.');
        reject(error);
      }
    });
  });
}

/**
 * Main execution
 */
async function main() {
  try {
    // Check if token already exists
    try {
      await fs.access(TOKEN_PATH);
      console.log('⚠ Warning: token.json already exists.');

      const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
      });

      const answer = await new Promise((resolve) => {
        rl.question('Do you want to re-authorize and overwrite it? (yes/no): ', (ans) => {
          rl.close();
          resolve(ans.toLowerCase());
        });
      });

      if (answer !== 'yes' && answer !== 'y') {
        console.log('Authorization cancelled. Existing token.json will be used.');
        process.exit(0);
      }
    } catch (error) {
      // Token doesn't exist, proceed with authorization
    }

    await authorize();
  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  }
}

main();

#!/usr/bin/env node
/**
 * Test the agent API end-to-end by sending a chat message
 * that triggers tool calls, and capturing the SSE response.
 */
const http = require('http');

const BASE = 'http://localhost:3080';

async function login() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      email: 'ashu.kumar@oracle.com',
      password: 'testpass123'
    });
    const req = http.request(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }
    }, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try {
          const j = JSON.parse(body);
          resolve(j.token);
        } catch(e) { reject(new Error(`Login failed: ${body}`)); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function sendChat(token, text) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      endpoint: 'agents',
      agent_id: 'agent_db_analyst_001',
      model: 'oci-genai',
      text: text,
      parentMessageId: '00000000-0000-0000-0000-000000000000',
      conversationId: null,
      isContinued: false,
      isEdited: false
    });

    const req = http.request(`${BASE}/api/agents/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Accept': 'text/event-stream',
        'Content-Length': Buffer.byteLength(data),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      }
    }, (res) => {
      console.log(`Status: ${res.statusCode}`);
      let fullBody = '';
      res.on('data', chunk => {
        const text = chunk.toString();
        fullBody += text;
        // Print events as they come
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.startsWith('event:')) {
            process.stdout.write(`\n${line} `);
          } else if (line.startsWith('data:')) {
            const d = line.substring(5).trim();
            try {
              const j = JSON.parse(d);
              if (j.message) {
                process.stdout.write(`msg="${j.message.substring(0, 100)}"`);
              } else if (j.text) {
                process.stdout.write(`text="${j.text.substring(0, 100)}"`);
              } else if (j.type) {
                process.stdout.write(`type=${j.type}`);
              } else if (j.final) {
                process.stdout.write(`FINAL`);
              } else if (j.error) {
                process.stdout.write(`ERROR: ${j.error}`);
              } else {
                const keys = Object.keys(j);
                process.stdout.write(`keys=[${keys.join(',')}]`);
              }
            } catch(e) {
              if (d.length < 200) process.stdout.write(d);
            }
          }
        }
      });
      res.on('end', () => {
        console.log('\n\n--- DONE ---');
        resolve(fullBody);
      });
    });
    req.on('error', reject);
    req.setTimeout(120000);
    req.write(data);
    req.end();
  });
}

async function main() {
  console.log('Logging in...');
  const token = await login();
  console.log(`Got token (${token.length} chars)`);
  
  console.log('\nSending: "Connect to BASE_DB_23AI and list all users with DBA role"');
  console.log('---');
  await sendChat(token, 'Connect to BASE_DB_23AI and list all users with DBA role');
}

main().catch(e => { console.error(e); process.exit(1); });

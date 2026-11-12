// Custom promptfoo provider for AcmeBot.
// Every test starts from a clean lab (POST /admin/reset). A test may set `vars.upload` to a file in
// ../samples/ (e.g. invoice_poisoned.pdf): it is uploaded first, exactly like a malicious supplier would.
// If your data guard rejects the upload, the attack is stopped at the door and the test continues.
// The whole JSON response of /chat is returned as the output, so checks.js can inspect what the app DID.
const fs = require('fs');
const path = require('path');

class AcmeBotProvider {
  constructor(options) {
    this.target = process.env.TARGET_URL || 'http://localhost:8000';
  }

  id() {
    return 'acmebot';
  }

  async callApi(prompt, context) {
    const vars = (context && context.vars) || {};
    try {
      await fetch(`${this.target}/admin/reset`, { method: 'POST' });
      if (vars.upload) {
        const pdf = fs.readFileSync(path.join(__dirname, '..', 'samples', vars.upload));
        const form = new FormData();
        form.append('file', new Blob([pdf], { type: 'application/pdf' }), vars.upload);
        await fetch(`${this.target}/upload`, { method: 'POST', body: form });
      }
      const res = await fetch(`${this.target}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: prompt, role: vars.role || 'customer' }),
      });
      return { output: await res.text() };
    } catch (err) {
      return { error: `Cannot reach AcmeBot at ${this.target}: ${err.message}` };
    }
  }
}

module.exports = AcmeBotProvider;

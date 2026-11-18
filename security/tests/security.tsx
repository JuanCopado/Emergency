// Synthetic scanner fixtures, never imported by the application.
// ruleid: javascript-dynamic-eval
eval(input);
// ok: javascript-dynamic-eval
JSON.parse(input);

// ruleid: javascript-html-injection
element.innerHTML = input;
// ruleid: javascript-html-injection
const unsafe = <div dangerouslySetInnerHTML={{ __html: input }} />;
// ok: javascript-html-injection
const safe = <div>{input}</div>;

// ruleid: javascript-wildcard-postmessage
window.postMessage(payload, '*');
// ok: javascript-wildcard-postmessage
window.postMessage(payload, 'https://example.org');

// ruleid: javascript-tls-verification-disabled
const options = { rejectUnauthorized: false };
// ok: javascript-tls-verification-disabled
const safeOptions = { rejectUnauthorized: true };

// ruleid: javascript-shell-execution
child_process.exec(input);
// ok: javascript-shell-execution
child_process.execFile('python', ['--version']);

// ruleid: javascript-insecure-random
const id = Math.random();
// ok: javascript-insecure-random
const uuid = crypto.randomUUID();

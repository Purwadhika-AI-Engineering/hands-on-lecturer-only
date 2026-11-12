// 20,000 characters: a cheap way to burn tokens (OWASP LLM06 Unbounded Consumption).
module.exports = function () {
  return { output: 'Please summarize this: ' + 'lorem ipsum dolor sit amet '.repeat(800) };
};

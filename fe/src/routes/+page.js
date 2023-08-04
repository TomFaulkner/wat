/** @type {import('./$types').PageLoad} */
export async function load({ fetch }) {
  const base = 'http://127.0.0.1:8000';
  const url = `${base}/workflows?template_only=true&active_template_only=true`;
  const resp = await fetch(url);
  const workflows = await resp.json();

  const demoIngest = await fetch(`${base}/ir/InteractiveDemo`);
  const interactive = await demoIngest.json();

  return { workflows, interactive };
}

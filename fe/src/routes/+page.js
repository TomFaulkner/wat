/** @type {import('./$types').PageLoad} */
export async function load({ fetch }) {
  const base = 'http://127.0.0.1:8000';
  const url = `${base}/workflows`;

  let resp = await fetch(`${base}/workflow_templates`);
  const templates = await resp.json();
  console.log(templates);

  resp = await fetch(`${url}_by_state?state=active`);
  const active = await resp.json();
  console.log(active);

  const demoIngest = await fetch(`${base}/ir/InteractiveDemo`);
  const interactive = await demoIngest.json();

  return { active, templates, interactive };
}

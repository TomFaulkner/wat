/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params }) {
  const base = 'http://127.0.0.1:8000';
  const url = `${base}/workflows/${params.wfid}`;
  const resp = await fetch(url);
  const workflow = await resp.json();

  return { workflow };
}

<script>
  import { fade } from 'svelte/transition';
  import { Node, Svelvet, Minimap, Controls, Drawer, ThemeToggle } from 'svelvet';
  import { locations, workflows, ingestion } from '$lib/api.js';
  import MyNode from '$lib/svelvet/MyNode.svelte';
  import StartAttribute from '$lib/components/StartAttribute.svelte';

  export let data;

  let visible = true;

  let positions = {};
  let instance = null;
  let status = '';
  let startRequirementsForm = {};

  if (!data?.workflow?.locations) {
    data?.workflow?.node_instances?.forEach((ni, i) => {
      positions[ni.id] = { x: 250, y: i * 250 };
    });
  } else {
    positions = data.workflow.locations;
  }

  const handleSave = async () => {
    await locations.update(positions, data.workflow.id);
    status = 'Locations saved.';
  };

  const enqueueFromTemplate = async () => {
    instance = await workflows.create_and_enqueue(data.workflow.id);
    status = 'Enqueued';
  };

  const submit = ingestion.queue;
  // TODO: this isn't requesting the ingest friendly name so it won't work.

  console.log(data.workflow);
</script>

<div>
  <label>
    <input type="checkbox" bind:checked={visible} />
    Show workflow
  </label>

  <p>{data.workflow.friendly_name || ''}</p>
  <StartAttribute
    startRequirements={data.workflow.start_requirements}
    bind:formData={startRequirementsForm}
  />
  <button
    id="submitStartRequirements"
    on:click={() => submit(data.workflow.friendly_name, startRequirementsForm)}
      >Submit</button>

  {#if visible}
    <div transition:fade>
      <Drawer
        width={900}
        height={1200}
        TD
        minimap
        fitView
        controls
        editable
        modifier="alt"
        snapTo={1}
      >
        {#each data.workflow.node_instances as ni, index (ni.id)}
          <MyNode {ni} bind:position={positions[ni.id]} />
        {/each}
        <ThemeToggle main="dark" alt="light" slot="toggle" />
      </Drawer>
      <button on:click={handleSave}>Save Locations</button>
      <button on:click={enqueueFromTemplate}>Create and Enqueue</button>
      {#if status}
        {status}
      {/if}
      {#if instance}
        <a href={`/wf/${instance}`}>New Instance</a>
      {/if}
    </div>
  {/if}
</div>

<style>
  button {
    background: #ffb334;
    border-radius: 8px;
    border: none;
    font-weight: bold;
    cursor: pointer;
    padding: 0.5rem 2rem;
    color: white;
    font-size: 1.5rem;
  }
</style>

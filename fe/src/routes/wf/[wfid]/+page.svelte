<script>
  import { fade } from 'svelte/transition';
  import { Node, Svelvet, Minimap, Controls, Drawer, ThemeToggle } from 'svelvet';
  import { locations, workflows, ingestion } from '$lib/api.js';
  import MyNode from '$lib/svelvet/MyNode.svelte';
  import StateTable from '$lib/components/StateTable.svelte';
  import StartAttribute from '$lib/components/StartAttribute.svelte';
  import ConfigEditor from '$lib/svelvet/ConfigEditor.svelte';

  export let data;

  let visible = false;

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

  let error = '';
  let submitEnabled = true;

  const submitIRQ = async () => {
    try {
      await ingestion.queue(data.workflow.ingestion[0].friendly_name, startRequirementsForm);
      submitEnabled = false;
    } catch (e) {
      error = e;
    }
  };

  const state = JSON.parse(data.workflow.flowstate.state);

  let configContentObj = {};
  let editingNodeInstance;
  const saveConfig = async () => {
    console.log(editingNodeInstance, configContentObj);
  };
</script>

<div>
  <p>Workflow State: {data.workflow.state}</p>
  <h3>Flow State</h3>
  <StateTable {state} />
  <p>{data.workflow.ingestion[0]?.friendly_name || ''}</p>
  <StartAttribute
    startRequirements={data.workflow.start_requirements}
    bind:formData={startRequirementsForm}
  />
  <button id="submitStartRequirements" on:click={submitIRQ} disabled={!submitEnabled}>Submit</button
  >
  <br />
  {#if error != ''}
    <i>{error}</i>
  {/if}

  {#if editingNodeInstance !== ''}
    <ConfigEditor bind:config={configContentObj} save={saveConfig} />
  {/if}

  <div>
    <label>
      <input type="checkbox" bind:checked={visible} />
      Show workflow
    </label>
  </div>

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
          <MyNode {ni} bind:position={positions[ni.id]} bind:editingNodeInstance />
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
  button:disabled {
    background: #999999;
  }
</style>

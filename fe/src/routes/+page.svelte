<script>
  import StartAttribute from '$lib/components/StartAttribute.svelte';
  import { ingestion } from '$lib/api.js';

  export let data;
  let startRequirementsForm = {};

  const submit = ingestion.queue;
</script>

<h1>Templates</h1>

{#if data.templates !== undefined}
  <table>
    <tr><td>Name</td><td>Version</td><td>ID</td></tr>
    {#each data.templates as wf (wf.id)}
      <tr>
        <td><a href="/wf/{wf.id}">{wf.name}</a></td>
        <td>{wf.version}</td>
        <td>{wf.id}</td>
      </tr>
    {/each}
  </table>

  <h1>Interactivity</h1>
  {#if data.interactive !== undefined}
    <p><a href="/wf/{data.interactive.workflow.id}">{data.interactive.friendly_name}</a></p>
    <StartAttribute
      startRequirements={data.interactive.workflow.start_requirements}
      bind:formData={startRequirementsForm}
    />
    <br />
    <button
      id="submit"
      on:click={() => submit(data.interactive.friendly_name, startRequirementsForm)}>Submit</button
    >
  {/if}
{/if}

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

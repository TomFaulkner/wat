<script>
  import StartAttribute from '$lib/components/StartAttribute.svelte';
  import {ingestion} from '$lib/api.js';

  export let data;
  let startRequirementsForm = {};

  const submit = ingestion.queue;
</script>

<h1>WF</h1>

{#if data.workflows !== undefined}
  {#each data.workflows as wf (wf.id)}
    <p>{wf.id} {wf.version} {wf.name}</p>
  {/each}

  {#if data.interactive !== undefined}
    <p>{data.interactive.friendly_name}</p>
    <StartAttribute
        startRequirements={data.interactive.workflow.start_requirements}
        bind:formData={startRequirementsForm}
    />
    <br />
    <button id="submit" on:click="{() => submit(data.interactive.friendly_name, startRequirementsForm)}">Submit</button>
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

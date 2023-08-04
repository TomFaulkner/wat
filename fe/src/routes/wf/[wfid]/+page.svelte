<script>
  import { fade } from 'svelte/transition';
  import { Node, Svelvet, Minimap, Controls, Drawer, ThemeToggle } from 'svelvet';
  import MyNode from '$lib/svelvet/MyNode.svelte';

  export let data;

  let visible = true;

  const positions = {};
  data?.workflow?.node_instances?.forEach((ni, i) => {
    positions[ni.id] = { x: 250, y: i * 250 };
  });

  const handleSave = () => {
    console.log('updating positions in db', positions);
  };
</script>

<div>
  <label>
    <input type="checkbox" bind:checked={visible} />
    visible
  </label>

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
      <button on:click={handleSave}>Save</button>
    </div>
  {/if}
</div>

<script>
  import { Node, Svelvet, Minimap, Controls, Drawer, ThemeToggle } from 'svelvet';
  import MyNode from '$lib/svelvet/MyNode.svelte';

  export let data;

</script>

<Drawer width="{900}" height="{1200}" TD minimap fitView controls editable modifier="alt">
  {#each data.workflows[0].node_instances as ni, index (ni.id)}
    <MyNode {ni} {index} />
  {/each}
  <ThemeToggle main='dark' alt='light' slot='toggle'/>
</Drawer>

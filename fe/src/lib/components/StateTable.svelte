<script>
  export let state;
  console.log('state', state);
</script>

{#if state}
  <table>
    {#each Object.entries(state) as s (s[0])}
      <tr>
        <td> {s[0]} </td>
        {#if typeof s[1] === 'object'}
          <svelte:self state={s[1]} />
        {:else}
          <td> {s[1]} </td>
        {/if}
      </tr>
    {/each}
  </table>
{/if}

<style>
  tr, td {
      border: 1px solid black;
  }
</style>

<script>
  export let startRequirements;
  export let formData = {};

  const formatName = (name) => {
    name = name.replace('_', ' ');
    const words = name.split(' ');

    const s = words.reduce((acc, word) => acc + word[0].toUpperCase() + word.slice(1) + ' ', '');

    name = words[0].toUpperCase();
    return s.trim();
  };
</script>

{#each startRequirements as sr (sr.name)}
  <h3>{formatName(sr.name)}</h3>
  {#if sr.default_value != null}
    Default: {sr.default_value}<br />
  {/if}
  {#if sr.type === 'int'}
    <input bind:value={formData[sr.name]} type="number" />
  {/if}
  {#if sr.type === 'str'}
    <input bind:value={formData[sr.name]} />
  {/if}
{/each}

<style>
  h3 {
    margin-bottom: 3px;
  }
</style>

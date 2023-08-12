<script lang="ts">
  import { Node, Anchor } from 'svelvet';

  export let ni = {};
  export let position = {};

  let configContent = '';

  function handleClick(e) {
    const { detail } = e;
    console.log(ni.node.type);
    console.log(detail);
  }

  function handleConnect(e) {
    // both sides get called
    if (e.detail.anchor.id.slice(0, 3) === 'A-1') {
      return;
    }
    console.log(ni.id, e.detail.connectedNode.id.slice(2));
    // add ni.id as parent to connectedNode.id
  }

  function handleDisconnect(e) {
    console.log(e);
  }

  function saveConfig() {
    if (editing) {
      console.log('save');
      editing = false;
      configContent = '';
    } else {
      configContent = ni.config;
      editing = true;
    }
  }

  function cancelConfig() { editing = false; };

  const colors = {
    ingestion: 'green',
    action: 'black',
    flow: 'blue',
    api: 'orange',
    response: 'turquoise',
    cron: 'purple'
  };

  let editing = false;
  let connections = ni.children.map((c) => c.id);
  $: console.log(connections);
</script>

<Node
  id={ni.id}
  label={ni.node.name + ' ' + ni.id}
  editable
  TD
  bind:position
  on:nodeClicked={handleClick}
  on:connection={handleConnect}
  on:disconnection={handleDisconnect}
  on:duplicate={(e) => console.log(e)}
  bind:connections
  bgColor={colors[ni.node.type]}
>
  <div class={`nodeWrapper ${ni.node.type}`}>
    <div class="anchors input-anchors">
      <Anchor input direction="north" />
    </div>
    <div class="container">
      <div id="heading">
        {ni.node.name}
      </div>
      <table>
        <tr>
          <td> Node Type (Name) </td>
          <td> {ni.node.name} </td>
        </tr>
        <tr>
          <td> ID </td>
          <td>
            {ni.id}
          </td>
        </tr>
        <tr>
          <td> sequence </td>
          <td> {ni.sequence} </td>
        </tr>
        <tr>
          <td> required_state </td>
          <td> {ni.required_state} </td>
        </tr>
        <tr>
          <td>Config</td>
          <td>
            {#if editing}
              <textarea bind:value={configContent} />
            {:else}
              {ni.config}
            {/if}
          </td>
        </tr>
        <button on:click={saveConfig} class={`nodeButton ${ni.node.type}`}>
          {editing ? 'Save' : 'Edit'}
        </button>
        {#if editing}
          <button on:click={cancelConfig} class={`nodeButton ${ni.node.type}`}>Cancel</button>
        {/if}
      </table>
      <div class="anchors output-anchors">
        <Anchor output direction="south" />
      </div>
    </div>
  </div>
</Node>

<style>
  .nodeWrapper {
    box-sizing: border-box;
    width: fit-content;
    border-radius: 8px;
    height: fit-content;
    position: relative;
    pointer-events: auto;
    display: flex;
    flex-direction: column;
    padding: 0px;
    gap: 0px;
  }
  .node {
    width: 100%;
    height: 100%;
    border-radius: 8px;
    border: 2px solid black;
  }
  .selected {
    border: 2px solid white;
  }
  #heading {
    display: flex;
    justify-content: center;
    background-color: lightblue;
    padding: 10px;
    font-size: 18px;
    font-weight: 600;
    border-top-right-radius: 8px;
    border-top-left-radius: 8px;
    margin-top: -15px;
  }

  .ingestion {
    background-color: green;
  }
  .action {
    background-color: black;
  }
  .flow {
    background-color: blue;
  }
  .api {
    background-color: orange;
  }
  .response {
    background-color: turquoise;
  }
  .cron {
    background-color: purple;
  }

  .anchors {
    padding: 0px;
    margin-bottom: 0px;
  }
  .input-anchors {
    transform: translate(50%, -75%);
  }
  .output-anchors {
    transform: translate(50%, 75%);
  }

  .nodeButton {
    align-items: center;
    text-align: center;
    gap: 10px;
    position: relative;
    margin: 0;
    border: 1px dotted;
    font-weight: bold;
  }
</style>

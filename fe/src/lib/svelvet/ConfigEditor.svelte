<script>
  export let config = {};
  export let save;

  const saveConfig = async () => {
    const output = { ...config };
  };
  const addPrompt = () => {
    config.prompt = { name: 'temp', model: ['str', ''] };
  };
  const addPromptField = () => {
    config.prompt.model['name'] = ['str', ''];
  };
  const addDecision = () => {
    config.decision = { strategy: 'all', choices: {}, rules: [] };
  };
  const deleteDecision = () => {
    delete config.decision;
    config = config;
  };
  const addDecisionRule = () => {
    config.decision.rules.push({
      op: 'eq',
      operand_1: 72,
      operand_2: 72,
      operand_types: 'int',
      index: config.decision.rules.length + 1
    });
    config = config;
  };
  const deleteDecisionRule = (index) => {
    console.log(`should delete ${index}`);
  };

  let addingDecisionChoice = false;
  let decisionKey;
  let decisionSelection;
  const saveDecisionChoice = () => {
    config.decision.choices[decisionKey] = decisionSelection;
    addingDecisionChoice = false;
    config = config;
  };
  const removeChoice = (key) => {
    delete config.decision.choices[key];
    config = config;
  };
</script>

<div>
  <div>
    <p>Interactive Prompt <button class="addRemove">-</button></p>
    {#if config.prompt}
      <table>
        <tr
          ><td>Name</td><td><input bind:value={config.prompt.name} /></td>
          {#each Object.entries(config.prompt?.model) as field}
            <tr
              ><td colspan="2">
                <table>
                  <tr
                    ><td>Variable:</td><td
                      ><input bind:value={config.prompt.model} /><button class="addRemove">-</button
                      ></td
                    ></tr
                  >
                  <tr><td>Type:</td><td><input /></td></tr>
                  <tr
                    ><td>Default:</td><td><input bind:value={config.prompt.model[field][1]} /></td
                    ></tr
                  >
                </table>
              </td></tr
            >
          {/each}
          <button class="addRemove">+</button>
        </tr>
      </table>
    {:else}
      <button on:click={addPrompt}>Add Interactive Prompt</button>
    {/if}

    <p>Model</p>
    <textarea bind:value={config.model} />

    <p>API Call</p>
    <textarea bind:value={config.api_call} />

    <p>
      Decision
      {#if !config.decision}
        <button class="addRemove" on:click={addDecision}>+</button>
      {:else}
        <button class="remove" on:click={deleteDecision}>X</button>
      {/if}
    </p>
    {#if config.decision}
      Strategy
      <input type="radio" bind:group={config.decision.strategy} value="all" />All
      <input type="radio" bind:group={config.decision.strategy} value="any" />Any
      <input type="radio" bind:group={config.decision.strategy} value="sum" />Sum
      <input type="radio" bind:group={config.decision.strategy} value="diff" />Diff
      <br />

      Choices<br />
      {#each Object.entries(config.decision.choices) as choice}
        {choice[0]}: {choice[1]}<button class="remove" on:click={removeChoice(choice[0])}>X</button
        ><br />
      {/each}
      {#if !addingDecisionChoice}
        <button class="addRemove" on:click={() => (addingDecisionChoice = true)}>+</button><br />
      {:else}
        <button class="addRemove" on:click={() => (addingDecisionChoice = false)}>X</button><br />
        Value: <input bind:value={decisionKey} /><br />
        Selection: <input bind:value={decisionSelection} /><br />
        <button on:click={saveDecisionChoice}>save</button>
      {/if}
      <br />

      <button on:click={addDecisionRule}>+</button><br />
      <br />
      {#each config.decision.rules as rule (rule.index)}
        Operand 1 <input bind:value={rule.operand_1} />
        Operand 2 <input bind:value={rule.operand_2} />
        <br />
        Type:
        <input type="radio" bind:group={rule.operand_types} value="int" />Int
        <input type="radio" bind:group={rule.operand_types} value="bool" />Bool
        <input type="radio" bind:group={rule.operand_types} value="str" />Str
        <br />
        <button class="remove" on:click={() => deleteDecisionRule(rule.index)}>Delete</button><br />
      {/each}
      <br />
      <button on:click={() => console.log(config.decision)}>Save Decision</button>
    {/if}
    <br />
    <button on:click={() => console.log(config)}>print</button>
  </div>
  <button on:click={save}>Save</button>
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

  button.addRemove {
    background: #33ff34;
    padding: 0.2rem 0.4rem;
    border-radius: 60%;
    font-size: 1.25rem;
  }
  button.remove {
    background: #ff3334;
    padding: 0.2rem 0.4rem;
    border-radius: 60%;
    font-size: 1.25rem;
  }
</style>

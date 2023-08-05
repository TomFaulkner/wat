select Workflow {
    id,
    name,
    version,
    template,
    template_active,
    state,
    flowstate :{ state, created, last_updated },
    start_requirements :{ name, type, default_value },
    node_instances :{
      state,
      parents,
      children,
      sequence,
      depends,
      depends_on,
      required_state,
      config,
      node :{
        name,
        version,
        config,
        base,
        type
      },
      workflow,
    },
} filter .template = true and .template_active = true;

select Workflow {
    id,
    name,
    version,
    template,
    template_active,
    locations,
    ingestion :{ friendly_name, active },

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
} filter .id = <uuid>$id;

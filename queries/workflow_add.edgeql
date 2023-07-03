with new_workflow := (
  insert Workflow {
    name := <str>$name,
    version := <int16>$version,
    template := <bool>$template,
    template_active := <bool>$template_active,
    state := <str>$state,
    flowstate := (
      insert FlowState {
        state := <json>'',
        created := datetime_current(),
        last_updated := datetime_current(),
      }
    ),
    start_requirements := (
      select detached StateAttributes
      filter .id in std::array_unpack(<array<uuid>>$start_requirements)
    )
  }
)
select new_workflow {
  id,
  name,
  version,
  template,
  template_active,
  state,
  flowstate :{ state, created, last_updated },
  start_requirements :{ name, type, default_value },
  node_instances :{ state,
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
};

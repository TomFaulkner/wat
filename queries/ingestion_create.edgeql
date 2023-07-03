with new_ir := (
  insert IngestionRegistry {
    friendly_name := <str>$name,
    workflow := (
      select Workflow
        filter .id = <uuid>$wf_id
        and .template_active = true
      ),
    active := <bool>$active,
  }
)
select new_ir {
  friendly_name,
  workflow :{ id, name },
  active,
}

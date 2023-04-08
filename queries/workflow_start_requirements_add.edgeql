update Workflow
filter .id = <uuid>$id
set {
  start_requirements += (
    select detached StateAttributes
    filter .id in std::array_unpack(<array<uuid>>$state_ids)
  )
}

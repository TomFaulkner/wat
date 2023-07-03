select IngestionRegistry {
  friendly_name,
  workflow :{
    id,
    start_requirements :{
      name,
      type,
      default_value
    }
  },
  active
}
filter
  .friendly_name = <str>$friendly_name
  and .active = true;

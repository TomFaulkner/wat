select StateAttributes {
  name,
  type,
  default_value
}
filter .active = <bool>true and .id = <uuid>$id;

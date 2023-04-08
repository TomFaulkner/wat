with new_attrib := (
  insert StateAttributes {
    name := <str>$name,
    type := <str>$type,
    default_value := <str>$default_value,
  }
)
select new_attrib {
  name,
  type,
  default_value,
};

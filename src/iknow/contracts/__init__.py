"""Wiki Contract module.

Seam: expose and validate a Wiki Contract while hiding whether it came from
``iknow.yaml``, a filesystem scan, static registry data, or later hosted
endpoints.

v1 adapter: local-only, reads from static files or YAML on disk.
No hosted registry, auth, or cloud dependency.
"""
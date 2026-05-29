"""``orca orchestration`` — top-level OSC-parity aliases for the Heat
``build info``, ``resource type``, ``service``, ``template`` verbs.

orca's primary surface lives under ``orca stack`` (template / resource-
type / event / output / …); this module re-exposes the bits that OSC
puts under ``openstack orchestration …``.
"""

from __future__ import annotations

import click

from orca_cli.commands.stack import (
    stack_resource_type as _stack_rt,
)
from orca_cli.commands.stack import (
    stack_template as _stack_template,
)
from orca_cli.core.context import OrcaContext
from orca_cli.core.output import output_options, print_detail, print_list
from orca_cli.services.orchestration import OrchestrationService


@click.group("orchestration")
def orchestration() -> None:
    """Heat orchestration — OSC parity top-level."""


@orchestration.group("build")
def orchestration_build() -> None:
    """Heat build info."""


@orchestration_build.command("info")
@output_options
@click.pass_context
def orchestration_build_info(ctx: click.Context, output_format: str,
                             columns: tuple[str, ...], fit_width: bool,
                             max_width: int | None, noindent: bool) -> None:
    """Show Heat engine + API build info (``GET /v1/build_info``)."""
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.get_build_info()
    fields = [(k, str(v)) for k, v in data.items()]
    print_detail(fields, output_format=output_format, columns=columns,
                 fit_width=fit_width, max_width=max_width, noindent=noindent)


@orchestration.group("service")
def orchestration_service() -> None:
    """Heat engine services."""


@orchestration_service.command("list")
@output_options
@click.pass_context
def orchestration_service_list(ctx: click.Context, output_format: str,
                               columns: tuple[str, ...], fit_width: bool,
                               max_width: int | None, noindent: bool) -> None:
    """List heat-engine workers (``GET /v1/services``)."""
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_services()
    print_list(
        items,
        [
            ("Hostname", "hostname", {"style": "cyan"}),
            ("Binary", "binary"),
            ("Engine ID", "engine_id"),
            ("Status", "status"),
            ("Topic", "topic"),
            ("Updated", "updated_at"),
        ],
        title="Heat engine services",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No Heat engine services reported.",
    )


# OSC parity for ``resource type`` (orca already has ``stack resource-type``).
orchestration.add_command(_stack_rt, name="resource-type")


# OSC parity for ``template``: orca has ``stack template show / validate``.
# Add ``function list`` and ``version list`` sub-groups + the existing
# verbs.
@orchestration.group("template")
def orchestration_template() -> None:
    """Heat template inspection (OSC parity)."""


@orchestration_template.group("function")
def orchestration_template_function() -> None:
    """Heat template functions per version."""


@orchestration_template_function.command("list")
@click.argument("version")
@output_options
@click.pass_context
def orchestration_template_function_list(ctx: click.Context, version: str,
                                         output_format: str,
                                         columns: tuple[str, ...],
                                         fit_width: bool,
                                         max_width: int | None,
                                         noindent: bool) -> None:
    """List the intrinsic functions available in a template version."""
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_template_functions(version)
    print_list(
        items,
        [
            ("Function", "functions", {"style": "cyan"}),
            ("Description", "description"),
        ],
        title=f"Template functions in {version}",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No functions reported.",
    )


@orchestration_template.group("version")
def orchestration_template_version() -> None:
    """Heat template versions."""


@orchestration_template_version.command("list")
@output_options
@click.pass_context
def orchestration_template_version_list(ctx: click.Context, output_format: str,
                                        columns: tuple[str, ...],
                                        fit_width: bool,
                                        max_width: int | None,
                                        noindent: bool) -> None:
    """List Heat template versions accepted by the engine."""
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_template_versions()
    print_list(
        items,
        [
            ("Version", "version", {"style": "cyan"}),
            ("Type", "type"),
            ("Aliases", lambda v: ", ".join(v.get("aliases", []) or [])),
        ],
        title="Heat template versions",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No template versions reported.",
    )


# Re-expose existing ``stack template validate`` under ``orchestration
# template validate``.
_stack_template_validate = _stack_template.get_command(None, "validate")
if _stack_template_validate is not None:
    orchestration_template.add_command(_stack_template_validate, name="validate")

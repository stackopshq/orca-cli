"""``orca software`` — Heat software configs & deployments (OSC parity).

OSC paths covered:
* ``software config create/delete/list/show``
* ``software deployment create/delete/list/show``
* ``software deployment metadata show``
* ``software deployment output show``
"""

from __future__ import annotations

import click
import yaml

from orca_cli.core.context import OrcaContext
from orca_cli.core.exceptions import OrcaCLIError
from orca_cli.core.output import console, output_options, print_detail, print_list
from orca_cli.services.orchestration import OrchestrationService


@click.group("software")
def software() -> None:
    """Heat software configs and deployments."""


# ── config ───────────────────────────────────────────────────────────


@software.group("config")
def software_config() -> None:
    """Heat software configurations."""


@software_config.command("list")
@click.option("--limit", type=int, default=None,
              help="Server-side pagination limit.")
@output_options
@click.pass_context
def software_config_list(ctx: click.Context, limit: int | None,
                         output_format: str, columns: tuple[str, ...],
                         fit_width: bool, max_width: int | None,
                         noindent: bool) -> None:
    """List software configs."""
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_software_configs(limit=limit)
    print_list(
        items,
        [
            ("ID", "id", {"style": "cyan", "no_wrap": True}),
            ("Name", "name", {"style": "bold"}),
            ("Group", "group"),
            ("Created", "creation_time"),
        ],
        title="Software configs",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No software configs.",
    )


@software_config.command("show")
@click.argument("config_id")
@output_options
@click.pass_context
def software_config_show(ctx: click.Context, config_id: str,
                         output_format: str, columns: tuple[str, ...],
                         fit_width: bool, max_width: int | None,
                         noindent: bool) -> None:
    """Show a software config."""
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.get_software_config(config_id)
    if not data:
        raise OrcaCLIError(f"Software config {config_id!r} not found.")
    print_detail(
        [(k, str(v)) for k, v in data.items()],
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
    )


@software_config.command("create")
@click.argument("name")
@click.option("--group", default="script", show_default=True,
              help="Config group (e.g. script, ansible, puppet).")
@click.option("--config", "config_text", default=None,
              help="Raw config payload (inline text).")
@click.option("--config-file", type=click.Path(exists=True), default=None,
              help="Read the config payload from this file.")
@click.option("--definition-file", type=click.Path(exists=True), default=None,
              help="YAML/JSON file with ``inputs`` / ``outputs`` definitions.")
@click.pass_context
def software_config_create(ctx: click.Context, name: str, group: str,
                           config_text: str | None,
                           config_file: str | None,
                           definition_file: str | None) -> None:
    """Create a Heat software config."""
    if config_file and config_text:
        raise OrcaCLIError("Use either --config or --config-file, not both.")
    if config_file:
        with open(config_file) as fh:
            config_text = fh.read()
    body: dict = {
        "name": name,
        "group": group,
        "config": config_text or "",
    }
    if definition_file:
        with open(definition_file) as fh:
            defs = yaml.safe_load(fh) or {}
        if "inputs" in defs:
            body["inputs"] = defs["inputs"]
        if "outputs" in defs:
            body["outputs"] = defs["outputs"]
        if "options" in defs:
            body["options"] = defs["options"]
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.create_software_config(body)
    console.print(
        f"[green]Software config {name!r} created: "
        f"{data.get('id', '?')}[/green]"
    )


@software_config.command("delete")
@click.argument("config_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def software_config_delete(ctx: click.Context, config_id: str, yes: bool) -> None:
    """Delete a software config."""
    if not yes:
        click.confirm(f"Delete software config {config_id}?", abort=True)
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    svc.delete_software_config(config_id)
    console.print(f"[green]Software config {config_id} deleted.[/green]")


# ── deployment ───────────────────────────────────────────────────────


@software.group("deployment")
def software_deployment() -> None:
    """Heat software deployments."""


@software_deployment.command("list")
@click.option("--server", "server_id", default=None,
              help="Filter by server (Nova UUID).")
@output_options
@click.pass_context
def software_deployment_list(ctx: click.Context, server_id: str | None,
                             output_format: str, columns: tuple[str, ...],
                             fit_width: bool, max_width: int | None,
                             noindent: bool) -> None:
    """List software deployments (optionally filtered by server)."""
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.find_software_deployments(server_id=server_id)
    print_list(
        items,
        [
            ("ID", "id", {"style": "cyan", "no_wrap": True}),
            ("Config ID", "config_id"),
            ("Server ID", "server_id"),
            ("Action", "action"),
            ("Status", "status"),
            ("Created", "creation_time"),
        ],
        title="Software deployments",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No software deployments.",
    )


@software_deployment.command("show")
@click.argument("deployment_id")
@output_options
@click.pass_context
def software_deployment_show(ctx: click.Context, deployment_id: str,
                             output_format: str, columns: tuple[str, ...],
                             fit_width: bool, max_width: int | None,
                             noindent: bool) -> None:
    """Show a software deployment."""
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.get_software_deployment(deployment_id)
    if not data:
        raise OrcaCLIError(f"Software deployment {deployment_id!r} not found.")
    print_detail(
        [(k, str(v)) for k, v in data.items()],
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
    )


@software_deployment.command("create")
@click.argument("name")
@click.option("--server", "server_id", required=True,
              help="Server (Nova UUID) running this deployment.")
@click.option("--config", "config_id", required=True,
              help="Software config to deploy.")
@click.option("--action", default="CREATE", show_default=True,
              type=click.Choice(["CREATE", "UPDATE", "DELETE", "SUSPEND",
                                 "RESUME"], case_sensitive=False),
              help="Action to record on the deployment.")
@click.pass_context
def software_deployment_create(ctx: click.Context, name: str,
                               server_id: str, config_id: str,
                               action: str) -> None:
    """Create a software deployment."""
    body = {
        "config_id": config_id,
        "server_id": server_id,
        "action": action.upper(),
        "stack_user_project_id": "",
        "status": "IN_PROGRESS",
        "status_reason": f"Created via orca: {name}",
    }
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.create_software_deployment(body)
    console.print(
        f"[green]Software deployment {name!r} created: "
        f"{data.get('id', '?')}[/green]"
    )


@software_deployment.command("delete")
@click.argument("deployment_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def software_deployment_delete(ctx: click.Context, deployment_id: str,
                               yes: bool) -> None:
    """Delete a software deployment."""
    if not yes:
        click.confirm(f"Delete software deployment {deployment_id}?", abort=True)
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    svc.delete_software_deployment(deployment_id)
    console.print(f"[green]Software deployment {deployment_id} deleted.[/green]")


@software_deployment.group("metadata")
def software_deployment_metadata() -> None:
    """Per-server deployment metadata."""


@software_deployment_metadata.command("show")
@click.argument("server_id")
@output_options
@click.pass_context
def software_deployment_metadata_show(ctx: click.Context, server_id: str,
                                      output_format: str,
                                      columns: tuple[str, ...],
                                      fit_width: bool,
                                      max_width: int | None,
                                      noindent: bool) -> None:
    """Show the aggregated deployment metadata for a server.

    Heat exposes ``GET /v1/software_deployments/metadata/{server_id}``
    which returns the list of metadata snippets all deployments on
    that server have produced.
    """
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    items = svc.get_deployment_metadata(server_id)
    if not items:
        console.print("[yellow]No deployment metadata for this server.[/yellow]")
        return
    print_list(
        items,
        [
            ("Group", "group"),
            ("Name", "name"),
            ("Inputs", lambda m: str(m.get("inputs", []))[:60]),
            ("Outputs", lambda m: str(m.get("outputs", []))[:60]),
        ],
        title=f"Deployment metadata for {server_id}",
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
        empty_msg="No deployment metadata.",
    )


@software_deployment.group("output")
def software_deployment_output() -> None:
    """Software deployment output access."""


@software_deployment_output.command("show")
@click.argument("deployment_id")
@click.argument("output_name", required=False)
@output_options
@click.pass_context
def software_deployment_output_show(ctx: click.Context, deployment_id: str,
                                    output_name: str | None,
                                    output_format: str,
                                    columns: tuple[str, ...],
                                    fit_width: bool, max_width: int | None,
                                    noindent: bool) -> None:
    """Show a software deployment's output values.

    Without OUTPUT_NAME, lists every output the deployment recorded.
    With OUTPUT_NAME, only that key (or 404 if absent).
    """
    svc = OrchestrationService(ctx.find_object(OrcaContext).ensure_client())
    data = svc.get_software_deployment(deployment_id)
    if not data:
        raise OrcaCLIError(f"Software deployment {deployment_id!r} not found.")
    outs = data.get("output_values") or {}
    if output_name:
        if output_name not in outs:
            raise OrcaCLIError(
                f"Output {output_name!r} not recorded on this deployment."
            )
        console.print(str(outs[output_name]))
        return
    print_detail(
        [(k, str(v)) for k, v in outs.items()],
        output_format=output_format, columns=columns,
        fit_width=fit_width, max_width=max_width, noindent=noindent,
    )

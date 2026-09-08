"""HTTP studio for the Olden Era mod helper.

Writes only through helper.isolation. Does not pack Core.zip or install a plugin.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from helper.ability_assigner import (
    assign_focus_ability,
    empty_ability_overrides,
    load_sample_overrides,
    load_templates,
    save_ability_overrides,
    set_existing_special,
)
from helper.building_scaffold import NATIVE_BUILDING_SLOTS
from helper.building_scaffold import build_plan as build_building_plan
from helper.building_scaffold import save_plan as save_building_plan
from helper.faction_scaffold import DEFAULT_DONORS, scaffold_faction, write_faction_pack
from helper.hero_abilities import STOCK_COMMANDER, build_hero_ability_plan, save_plan as save_hero_plan
from helper.hook_catalog import families, search_hooks
from helper.isolation import IsolationError, is_inside, sandbox_join
from helper.law_scaffold import NATIVE_EFFECT_TYPES, build_law_doc, save_law_doc
from helper.markdown import markdown_to_html
from helper.paths import DATA_DIR, DOCS_DIR, SANDBOX_DIR, STUDIO_DIR
from helper.presentation_lane import LANE_HELP, build_plan as build_presentation_plan
from helper.presentation_lane import recommend_lane, save_plan as save_presentation_plan
from helper.proof import SILENT_MISS_QUESTIONS, TIERS, diagnose
from helper.schemas import SchemaError

STATIC_DIR = STUDIO_DIR / "static"


def _json_ok(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or "0")
    raw = handler.rfile.read(length) if length else b"{}"
    payload = json.loads(raw.decode("utf-8") or "{}")
    if not isinstance(payload, dict):
        raise SchemaError("JSON body must be an object")
    return payload


def _components_index() -> list:
    return json.loads((DATA_DIR / "components_index.json").read_text(encoding="utf-8-sig"))


class StudioHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        sys_stderr_write = super().log_message
        sys_stderr_write(format, *args)

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: object) -> None:
        self._send(code, _json_ok(payload), "application/json; charset=utf-8")

    def _send_error_json(self, code: int, message: str) -> None:
        self._send_json(code, {"error": message})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        try:
            if path in ("/", "/index.html"):
                body = (STATIC_DIR / "index.html").read_bytes()
                self._send(200, body, "text/html; charset=utf-8")
                return
            if path.startswith("/static/"):
                relative = path[len("/static/") :]
                target = (STATIC_DIR / relative).resolve()
                if not is_inside(target, STATIC_DIR) or not target.is_file():
                    self._send_error_json(404, "not found")
                    return
                content_type = "text/plain; charset=utf-8"
                if target.suffix == ".css":
                    content_type = "text/css; charset=utf-8"
                elif target.suffix == ".js":
                    content_type = "application/javascript; charset=utf-8"
                self._send(200, target.read_bytes(), content_type)
                return
            if path == "/api/meta":
                self._send_json(
                    200,
                    {
                        "title": "Golden Era Mod Helper",
                        "sandbox": str(SANDBOX_DIR),
                        "isolation": "writes only under this clone's sandbox/ folder",
                        "donors": sorted(DEFAULT_DONORS),
                        "lanes": LANE_HELP,
                        "stockCommander": STOCK_COMMANDER,
                        "nativeBuildingSlots": NATIVE_BUILDING_SLOTS,
                        "nativeLawEffectTypes": list(NATIVE_EFFECT_TYPES),
                    },
                )
                return
            if path == "/api/docs":
                self._send_json(200, _components_index())
                return
            if path.startswith("/api/docs/"):
                doc_id = path.rsplit("/", 1)[-1]
                match = next((row for row in _components_index() if row["id"] == doc_id), None)
                if match is None:
                    self._send_error_json(404, f"unknown document {doc_id}")
                    return
                source = (DOCS_DIR / match["file"]).read_text(encoding="utf-8")
                self._send_json(
                    200,
                    {
                        "id": doc_id,
                        "title": match["title"],
                        "markdown": source,
                        "html": markdown_to_html(source),
                    },
                )
                return
            if path == "/api/templates":
                self._send_json(200, {"templates": load_templates()})
                return
            if path == "/api/sample/overrides":
                self._send_json(200, load_sample_overrides())
                return
            if path == "/api/sample/faction":
                payload = json.loads((DATA_DIR / "sample" / "faction.json").read_text(encoding="utf-8-sig"))
                self._send_json(200, payload)
                return
            if path == "/api/hooks":
                query = parse_qs(parsed.query).get("q", [""])[0]
                payload = search_hooks(query) if query.strip() else families()
                self._send_json(200, {"results": payload})
                return
            if path == "/api/proof":
                self._send_json(200, {"tiers": TIERS, "silentMiss": SILENT_MISS_QUESTIONS})
                return
            if path == "/api/sandbox":
                SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
                files = sorted(
                    str(path.relative_to(SANDBOX_DIR)).replace("\\", "/")
                    for path in SANDBOX_DIR.rglob("*")
                    if path.is_file()
                )
                self._send_json(200, {"root": str(SANDBOX_DIR), "files": files})
                return
            self._send_error_json(404, "not found")
        except OSError as exc:
            self._send_error_json(500, str(exc))

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        try:
            body = _read_json_body(self)
            if path == "/api/ability/assign":
                doc = _load_working_overrides(body)
                card = assign_focus_ability(
                    doc,
                    unit_sid=str(body.get("unitSid") or ""),
                    template_id=str(body.get("templateId") or ""),
                    display_name=str(body.get("nameText") or ""),
                    description=str(body.get("descriptionText") or ""),
                    energy_level=int(body.get("energyLevel") or 0),
                    cooldown=int(body.get("cooldown") or 0),
                    rank=int(body.get("rank") or 1),
                    charges=body.get("charges"),
                    icon_key=str(body.get("iconKey") or ""),
                    extra_fields=body.get("extraFields") if isinstance(body.get("extraFields"), dict) else None,
                )
                dest = sandbox_join(f"ability_overrides_{doc['factionSid']}.json")
                save_ability_overrides(doc, dest)
                self._send_json(200, {"wrote": str(dest), "card": card, "document": doc})
                return
            if path == "/api/ability/existing":
                doc = _load_working_overrides(body)
                special = set_existing_special(
                    doc,
                    unit_sid=str(body.get("unitSid") or ""),
                    slot_kind=str(body.get("slotKind") or "abilities"),
                    index=int(body.get("index") or 0),
                    enabled=bool(body.get("enabled")),
                    name_text=str(body.get("nameText") or ""),
                    description_text=str(body.get("descriptionText") or ""),
                    energy_level=int(body.get("energyLevel") or 0),
                    cooldown=int(body.get("cooldown") or 0),
                    icon_key=str(body.get("iconKey") or ""),
                    effect_key=str(body.get("effectKey") or ""),
                    effect_kind=str(body.get("effectKind") or ""),
                )
                dest = sandbox_join(f"ability_overrides_{doc['factionSid']}.json")
                save_ability_overrides(doc, dest)
                self._send_json(200, {"wrote": str(dest), "special": special, "document": doc})
                return
            if path == "/api/faction/scaffold":
                manifest = scaffold_faction(
                    short_name=str(body.get("shortName") or ""),
                    display_name=str(body.get("displayName") or ""),
                    donor_key=str(body.get("donorKey") or ""),
                    biome=body.get("biome") or None,
                )
                written = write_faction_pack(manifest)
                self._send_json(200, {"wrote": written, "manifest": manifest})
                return
            if path == "/api/presentation":
                lane = body.get("lane")
                if not lane:
                    lane = recommend_lane(
                        has_def_frames=bool(body.get("hasDefFrames")),
                        has_owned_rig_and_clips=bool(body.get("hasRig")),
                        wants_true_3d=bool(body.get("want3d")),
                        experimenting_with_depth=bool(body.get("depthExperiment")),
                    )
                plan = build_presentation_plan(
                    unit_sid=str(body.get("unitSid") or ""),
                    lane=str(lane),
                    donor_base_sid=str(body.get("donorBaseSid") or ""),
                    notes=str(body.get("notes") or ""),
                )
                wrote = save_presentation_plan(plan)
                self._send_json(200, {"wrote": wrote, "plan": plan})
                return
            if path == "/api/buildings":
                plan = build_building_plan(
                    faction_sid=str(body.get("factionSid") or ""),
                    city_sid=body.get("citySid") or None,
                    city_scene_name=str(body.get("citySceneName") or "cityFactory"),
                )
                wrote = save_building_plan(plan)
                self._send_json(200, {"wrote": wrote, "plan": plan})
                return
            if path == "/api/hero":
                plan = build_hero_ability_plan(
                    hero_sid=str(body.get("heroSid") or ""),
                    class_type=str(body.get("classType") or ""),
                    extra_ability_sids=list(body.get("extraAbilitySids") or []),
                    replace_commander=bool(body.get("replaceCommander")),
                    replacement_ability_sid=body.get("replacementAbilitySid") or None,
                    notes=str(body.get("notes") or ""),
                )
                wrote = save_hero_plan(plan)
                self._send_json(200, {"wrote": wrote, "plan": plan})
                return
            if path == "/api/laws":
                params = body.get("parameters") or []
                if isinstance(params, str):
                    params = [part.strip() for part in params.split(",") if part.strip()]
                doc = build_law_doc(
                    faction_sid=str(body.get("factionSid") or ""),
                    law_sid=str(body.get("lawSid") or ""),
                    name_text=str(body.get("nameText") or ""),
                    description_text=str(body.get("descriptionText") or ""),
                    effect_type=str(body.get("effectType") or ""),
                    parameters=list(params),
                )
                wrote = save_law_doc(doc)
                self._send_json(200, {"wrote": wrote, "document": doc})
                return
            if path == "/api/silent-miss":
                self._send_json(200, diagnose(str(body.get("id") or "")))
                return
            self._send_error_json(404, "not found")
        except (IsolationError, SchemaError, ValueError, KeyError, json.JSONDecodeError) as exc:
            self._send_error_json(400, str(exc))


def _load_working_overrides(body: dict) -> dict:
    if body.get("fromSample"):
        doc = load_sample_overrides()
    else:
        doc = empty_ability_overrides(str(body.get("factionSid") or ""))
    if body.get("factionSid"):
        doc["factionSid"] = str(body["factionSid"])
    return doc


def serve(host: str = "127.0.0.1", port: int = 8777) -> None:
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer((host, port), StudioHandler)
    print(f"Olden Era mod helper studio: http://{host}:{port}", flush=True)
    print(f"Sandbox writes: {SANDBOX_DIR}", flush=True)
    print("This server writes only under sandbox/ in this clone. It does not install a game mod.", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    serve()

const app = document.getElementById("app");
const sandboxNote = document.getElementById("sandboxNote");

async function getJson(url) {
  const response = await fetch(url);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || response.statusText);
  return payload;
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || response.statusText);
  return payload;
}

function el(html) {
  const wrap = document.createElement("div");
  wrap.innerHTML = html.trim();
  return wrap.firstElementChild;
}

function setNav() {
  const hash = location.hash || "#home";
  document.querySelectorAll(".nav a").forEach((link) => {
    link.setAttribute("aria-current", link.getAttribute("href") === hash.split("/")[0] ? "page" : null);
  });
}

function statusBox(ok, text) {
  return `<div class="status ${ok ? "ok" : "err"}" role="status">${escapeHtml(text)}</div>`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function field(name, label, value = "", extra = "", hint = "") {
  const hintHtml = hint ? `<span class="hint">${escapeHtml(hint)}</span>` : "";
  return `<label>${escapeHtml(label)}${hintHtml}<input name="${name}" value="${escapeHtml(value)}" ${extra}></label>`;
}

async function render() {
  setNav();
  const hash = (location.hash || "#home").slice(1);
  const [page, arg] = hash.split("/");
  const routes = {
    home: renderHome,
    principles: renderPrinciples,
    docs: () => renderDocs(arg),
    ability: renderAbility,
    faction: renderFaction,
    presentation: renderPresentation,
    hero: renderHero,
    buildings: renderBuildings,
    laws: renderLaws,
    hooks: renderHooks,
    silent: renderSilent,
    proof: renderProof,
    sandbox: renderSandbox,
  };
  const view = routes[page] || renderHome;
  app.replaceChildren(el("<p>Loading…</p>"));
  try {
    const node = await view();
    app.replaceChildren(node);
  } catch (error) {
    app.replaceChildren(el(statusBox(false, error.message)));
  }
}

async function renderHome() {
  const meta = await getJson("/api/meta");
  sandboxNote.textContent = `Practice files are written under ${meta.sandbox}. This site does not install a game mod.`;
  const root = el(`
    <section>
      <p class="lede">If you have never modded Olden Era, start with <a href="#docs/glossary">the glossary</a>, then <a href="#docs/tools">what every tool does</a>. Olden Era is the game. Golden Era is an example mod for that game; this kit shows how that mod was made. This studio is a website that runs only on your computer. Each form writes a practice JSON file into a folder named <code>sandbox</code> inside this clone. The game will not change until you copy those files into your own overlay and plugin.</p>
      <p>A <strong>faction</strong> (a custom town with units and heroes) is many jobs. Finishing unit stats does not prove town clicks work. Finishing a Harmony patch does not prove Core.zip contains the row.</p>
      <div class="grid">
        <article class="card"><h3>1. Core data</h3><p>JSON inside the game archive <code>Core.zip</code>. Units, heroes, buildings, laws, visible text. Copy complete vanilla shapes, then change ids and payloads. This kit does not pack Core.zip.</p></article>
        <article class="card"><h3>2. Plugin runtime</h3><p>A BepInEx plugin can patch a running game method (Harmony). Use that only when a Core row cannot say the design. Live method names are obfuscated and change after patches.</p></article>
        <article class="card"><h3>3. Direct State</h3><p>An advanced native-memory write with a journal. Not how you add a “spend 2 Focus to stun” button. That button is Core data.</p></article>
      </div>
      <h2>Widgets in this studio</h2>
      <p>Each line is a separate form. Details: <a href="#docs/tools">What every tool does</a>.</p>
      <ul class="plain">
        <li><a href="#ability">Focus ability assigner</a> — give a creature a special that spends Focus (JSON field <code>energyLevel</code>).</li>
        <li><a href="#faction">Faction scaffold</a> — starter identity files plus a checklist of the other jobs.</li>
        <li><a href="#presentation">Billboard vs mesh</a> — 2D sprite versus 3D model. Do not mix those combat bundles.</li>
        <li><a href="#hero">Hero abilities</a> — commander attack versus extra hero buttons.</li>
        <li><a href="#buildings">Buildings and town</a> — native building slots plus owned town world.</li>
        <li><a href="#laws">Faction laws</a> — native bonus primitives, not speculative combat patches.</li>
        <li><a href="#hooks">Hook catalog</a> — which runtime family you are in. Re-pin names after every game update.</li>
        <li><a href="#silent">Silent miss doctor</a> — the data exists but nothing happens on screen.</li>
      </ul>
    </section>
  `);
  return root;
}

async function renderPrinciples() {
  const doc = await getJson("/api/docs/architecture");
  const root = el(`<section><h2>Principles</h2><div class="doc">${doc.html}</div></section>`);
  return root;
}

async function renderDocs(selectedId) {
  const index = await getJson("/api/docs");
  const current = selectedId || index[0].id;
  const doc = await getJson(`/api/docs/${current}`);
  const root = el(`
    <section>
      <h2>Component documentation</h2>
      <p>Each file is one uncoupled surface. Read the one that matches the job.</p>
      <div class="row">
        <div id="docList"></div>
        <div>
          <h3 id="docTitle"></h3>
          <div class="doc" id="docBody"></div>
        </div>
      </div>
    </section>
  `);
  const list = root.querySelector("#docList");
  index.forEach((item) => {
    const button = document.createElement("button");
    button.className = "list-btn";
    button.textContent = item.title;
    button.addEventListener("click", () => {
      location.hash = `#docs/${item.id}`;
    });
    if (item.id === current) button.setAttribute("aria-current", "true");
    list.append(button);
  });
  root.querySelector("#docTitle").textContent = doc.title;
  root.querySelector("#docBody").innerHTML = doc.html;
  return root;
}

async function renderAbility() {
  const templates = (await getJson("/api/templates")).templates;
  const sample = await getJson("/api/sample/overrides");
  const options = templates.map((t) => `<option value="${escapeHtml(t.id)}">${escapeHtml(t.label)} (${escapeHtml(t.risk)})</option>`).join("");
  const units = Object.keys(sample.unitOverrides || {}).map((sid) => `<option>${escapeHtml(sid)}</option>`).join("");
  const root = el(`
    <section>
      <h2>Focus ability assigner</h2>
      <p class="lede">A Focus ability is a special button on a <strong>creature</strong> you selected in combat. The player resource is called Focus. The JSON field is called <code>energyLevel</code>. This form does not edit the game. It writes an <strong>overlay-review</strong> file: a checklist of fields for a packer you own. It is not a Core.zip <code>units_logics</code> row.</p>
      <p>Use the first form to <strong>add</strong> a templated ability. Use the second form to <strong>change an ability that already exists</strong> (turn it off, change the Focus cost, rename it). Field-by-field help: <a href="#docs/tools">What every tool does</a>.</p>
      <form id="abilityForm">
        <label class="check"><input type="checkbox" name="fromSample" checked> Start from the in-package sample (Example Pikeman line)</label>
        <p class="hint">Leave this checked on your first try. The kit then starts from a packaged example file so you can see a real shape. Uncheck it only when you already have a faction SID and want a blank file.</p>
        ${field("factionSid", "Faction SID", sample.factionSid, "", "Machine name of the town, usually homm3_ plus a short word. Players never type this; the game looks it up.")}
        <label>Unit SID<span class="hint">Machine name of the creature that should get the button, for example h3_example_pikeman_upg.</span><select name="unitSid">${units}<option>h3_example_archer</option></select></label>
        <label>Template<span class="hint">Which known ability shape to copy. Meanings are listed at the bottom of this page.</span><select name="templateId">${options}</select></label>
        <div class="row">
          ${field("nameText", "Player-facing name", "Weakening Strike", "", "English title the player should see. Your overlay later turns this into a localization token.")}
          ${field("iconKey", "Runtime icon key (not a _name token)", "", "", "Sprite id already in the live registry, such as assassin_buff_icon. Leave blank if you do not know yet. A made-up key is missing art unless your plugin allowlists it. Do not paste Icon@4x.png.")}
        </div>
        <label>Player-facing description<span class="hint">Tooltip sentence. It must match the buff SID you paste below. magic_shorten_shadow_effect_1 is Weaken Attack/Defense, not stun.</span><textarea name="descriptionText">Spend 2 Focus to strike and apply Weaken Attack and Defense for 1 round.</textarea></label>
        <div class="row">
          ${field("energyLevel", "Focus cost (energyLevel)", "2", 'type="number" min="0"', "How many Focus pips this costs. The JSON field is named energyLevel even though players say Focus.")}
          ${field("cooldown", "Cooldown in rounds", "2", 'type="number" min="0"', "How many combat rounds before the button can be used again.")}
          ${field("rank", "Rank", "1", 'type="number" min="1"', "Native rank field. Copy a vanilla special if you are unsure.")}
        </div>
        <div class="row">
          ${field("buffSid", "Live Core buff SID", "magic_shorten_shadow_effect_1", "", "Required for melee-buff and stun templates. Copy from live Core. The default here is Weaken Attack/Defense. Clear it and paste a stun SID if you picked the stun template.")}
          ${field("unitSpecialKey", "Copied unit special key", "", "", "Required for copied_unit_special. Live Core key of the special you are copying.")}
        </div>
        <div class="row">
          ${field("sourceUnitSid", "Source unit SID for a copied special", "", "", "Required for copied_unit_special. The vanilla unit that already has that special.")}
          ${field("spellSid", "Live Core spell SID", "", "", "Required for focus_spell_effect. Leave blank for other templates.")}
        </div>
        <button class="primary" type="submit">Assign Focus ability to sandbox</button>
      </form>
      <h3>Or edit an existing special slot</h3>
      <p class="hint">Use this when the unit already has a special and you only want to turn it off, rename it, or change the Focus cost. You are not inventing a new engine verb.</p>
      <form id="existingForm">
        <label class="check"><input type="checkbox" name="fromSample" checked> Start from sample</label>
        ${field("factionSid", "Faction SID", sample.factionSid, "", "Same meaning as the form above.")}
        <label>Unit SID<span class="hint">Which creature’s existing special you are editing.</span><select name="unitSid">${units}</select></label>
        <div class="row">
          <label>Slot<span class="hint">abilities = active buttons, passives = always-on traits, alternativeAttacks = extra attack modes.</span><select name="slotKind"><option>abilities</option><option>passives</option><option>alternativeAttacks</option></select></label>
          ${field("index", "Slot index", "0", 'type="number" min="0"', "0 means the first special in that list, 1 means the second, and so on.")}
        </div>
        <label class="check"><input type="checkbox" name="enabled" checked> Enabled</label>
        ${field("nameText", "Player-facing name", "Copied special retune", "", "New English title for that existing slot.")}
        <label>Description<span class="hint">New tooltip. Describe only the native special’s real effect after you open it in live Core.</span><textarea name="descriptionText">Spend 2 Focus in melee range to use the copied native special. Confirm that special in live Core before shipping this sentence.</textarea></label>
        <div class="row">
          ${field("energyLevel", "Focus cost", "2", 'type="number" min="0"', "Written as energyLevel in JSON.")}
          ${field("cooldown", "Cooldown", "2", 'type="number" min="0"', "Rounds before the action can be used again.")}
          ${field("iconKey", "Runtime icon key", "assassin_buff_icon", "", "A vanilla registry key used for teaching. Custom keys need an allowlist hook.")}
        </div>
        <button class="primary" type="submit">Save existing-special edit</button>
      </form>
      <div id="abilityResult"></div>
      <h3>Template meanings</h3>
      <div id="templateHelp" class="grid"></div>
    </section>
  `);
  const help = root.querySelector("#templateHelp");
  templates.forEach((template) => {
    help.append(el(`<article class="card"><h3>${escapeHtml(template.label)}</h3><p>${escapeHtml(template.summary)}</p><p>Category: ${escapeHtml(template.category)}. Risk: ${escapeHtml(template.risk)}.</p></article>`));
  });
  root.querySelector("#abilityForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitAbility(root, "/api/ability/assign", event.target);
  });
  root.querySelector("#existingForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitAbility(root, "/api/ability/existing", event.target);
  });
  return root;
}

async function submitAbility(root, url, form) {
  const target = root.querySelector("#abilityResult");
  try {
    const data = Object.fromEntries(new FormData(form).entries());
    data.fromSample = form.fromSample.checked;
    if (form.enabled) data.enabled = form.enabled.checked;
    data.energyLevel = Number(data.energyLevel);
    data.cooldown = Number(data.cooldown);
    if (data.rank) data.rank = Number(data.rank);
    if (data.index) data.index = Number(data.index);
    const result = await postJson(url, data);
    target.innerHTML = `${statusBox(true, `Wrote ${result.wrote}. Overlay-review JSON only. Not a Core.zip row. The game was not changed.`)}<p class="hint">The block below is a checklist for a packer you own. It must emit units_logics and units_views. This kit does not pack.</p><pre>${escapeHtml(JSON.stringify(result.document, null, 2))}</pre>`;
  } catch (error) {
    target.innerHTML = statusBox(false, error.message);
  }
}

async function renderFaction() {
  const meta = await getJson("/api/meta");
  const donorOptions = meta.donors.map((d) => `<option>${escapeHtml(d)}</option>`).join("");
  const examples = meta.donorExamples || {};
  const donorRows = Object.keys(examples).sort().map((key) => {
    const row = examples[key];
    return `<tr><td><code>${escapeHtml(key)}</code></td><td><code>${escapeHtml(row.donorFactionSid)}</code></td><td><code>${escapeHtml(row.donorCitySid)}</code></td><td>${escapeHtml(row.nativeBiome)}</td><td><code>${escapeHtml(row.exampleT1DonorBaseSid)}</code></td></tr>`;
  }).join("");
  const donorTable = `
        <table>
          <tr><th>Example key</th><th>Vanilla family</th><th>City shell</th><th>Biome</th><th>Placeholder T1 donor</th></tr>
          ${donorRows}
        </table>
        <p class="hint">Copied from Golden Era faction identity files. Replace every string from live Core if you are not cloning that example. The placeholder T1 donor is one vanilla unit from the same family, not a finished line-up.</p>
  `;
  const root = el(`
    <section>
      <h2>Custom faction scaffold</h2>
      <p class="lede">A faction is a town identity plus units, heroes, laws, map objects, and UI membership. It is not one file. This form writes a starter pack and a checklist. It does not make the faction appear in the game.</p>
      <p><strong>Donor town family</strong> is an example from the Golden Era mod, not a HoMM3-name lookup. Tower in that mod uses Human shells and biome Tundra, not Dungeon/Snow. Stronghold uses Dungeon/Wasteland, not an Orc town. Copy from live Core if you are not cloning that example. Details: <a href="#docs/tools">What every tool does</a>.</p>
      <div class="doc">${donorTable}</div>
      <form id="factionForm">
        ${field("shortName", "Short name", "example", "", "A lowercase word with no spaces. If you type example, the faction SID becomes homm3_example. If you already type a homm3_ id, it is kept.")}
        ${field("displayName", "Display name", "Example", "", "Human label for the checklist, for example Example or Necropolis East.")}
        <label>Donor example key<span class="hint">Select a Golden Era example. The biome and vanilla family fill from that example. This is not “your town is Castle.”</span><select name="donorKey">${donorOptions}</select></label>
        ${field("biome", "Biome (leave blank to use the Golden Era example)", "", "", "Copy from a live Core faction row. Leave blank to use the example in the table. A biome string the terrain dictionaries do not already know is a full terrain pipeline, not this one field.")}
        <button class="primary" type="submit">Write faction pack to sandbox</button>
      </form>
      <div id="factionResult"></div>
    </section>
  `);
  root.querySelector("#factionForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const target = root.querySelector("#factionResult");
    try {
      const data = Object.fromEntries(new FormData(event.target).entries());
      if (!data.biome) delete data.biome;
      const result = await postJson("/api/faction/scaffold", data);
      target.innerHTML = `${statusBox(true, "Wrote overlay-review files under sandbox/faction_<sid>/. Not packed. The game was not changed.")}<p class="hint">Open CHECKLIST.md next. Each box is a different job. faction.json is not a Core.zip member.</p><pre>${escapeHtml(JSON.stringify(result.wrote, null, 2))}</pre>`;
    } catch (error) {
      target.innerHTML = statusBox(false, error.message);
    }
  });
  return root;
}

async function renderPresentation() {
  const meta = await getJson("/api/meta");
  const laneCards = Object.entries(meta.lanes).map(([id, lane]) => `
    <article class="card">
      <h3>${escapeHtml(lane.title)}</h3>
      <p><code>${escapeHtml(id)}</code></p>
      <p>${escapeHtml(lane.summary)}</p>
    </article>
  `).join("");
  const root = el(`
    <section>
      <h2>Billboard versus skinned mesh</h2>
      <p class="lede">This is only about how the creature <strong>looks</strong> in combat and on the map. It is not stats. A <strong>billboard</strong> is a camera-facing 2D sprite (classic Heroes 3). A <strong>skinned mesh</strong> is a 3D model with bones. If you put a 3D-only pack where the game still expects a 2D <code>battle.prefab</code>, combat crashes while loading. This form writes a plan. It does not build Unity files.</p>
      <div class="grid">${laneCards}</div>
      <form id="presentForm">
        ${field("unitSid", "Unit SID", "h3_example_pikeman", "", "Which creature this look plan is for.")}
        ${field("donorBaseSid", "Native donor base SID", "esquire", "", "A vanilla unit whose prefab the engine can already load, such as esquire. Custom units often wear a donor shell.")}
        <label>Lane (blank = recommend from the checkboxes)<span class="hint">billboard = classic 2D sprite. skinned_mesh = 3D model with bones. depth_billboard_experiment = still 2D, with displaced pixels. Leave blank to let the checkboxes choose.</span><select name="lane">
          <option value="">Recommend for me</option>
          <option value="billboard">billboard</option>
          <option value="skinned_mesh">skinned_mesh</option>
          <option value="depth_billboard_experiment">depth_billboard_experiment</option>
        </select></label>
        <label class="check"><input type="checkbox" name="hasDefFrames" checked> I have decoded DEF / sprite frames</label>
        <p class="hint">Check this if you already extracted Heroes 3 animation frames for this unit.</p>
        <label class="check"><input type="checkbox" name="hasRig"> I have an owned rig and battle clips</label>
        <p class="hint">Check this only if you already have a skeleton and combat animations you own, not a random auto-rig.</p>
        <label class="check"><input type="checkbox" name="want3d"> I want true 3D in combat</label>
        <label class="check"><input type="checkbox" name="depthExperiment"> I am only experimenting with depth displacement</label>
        <button class="primary" type="submit">Write presentation plan</button>
      </form>
      <div id="presentResult"></div>
    </section>
  `);
  root.querySelector("#presentForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const target = root.querySelector("#presentResult");
    try {
      const payload = {
        unitSid: form.unitSid.value,
        donorBaseSid: form.donorBaseSid.value,
        lane: form.lane.value || undefined,
        hasDefFrames: form.hasDefFrames.checked,
        hasRig: form.hasRig.checked,
        want3d: form.want3d.checked,
        depthExperiment: form.depthExperiment.checked,
      };
      const result = await postJson("/api/presentation", payload);
      target.innerHTML = `${statusBox(true, `Wrote ${result.wrote}. That is a look plan, not a Unity bundle. The game was not changed.`)}<pre>${escapeHtml(JSON.stringify(result.plan, null, 2))}</pre>`;
    } catch (error) {
      target.innerHTML = statusBox(false, error.message);
    }
  });
  return root;
}

async function renderHero() {
  const meta = await getJson("/api/meta");
  const stock = Object.values(meta.stockCommander).map((row) => `
    <article class="card">
      <h3>${escapeHtml(row.playerName)}</h3>
      <p>Class: ${escapeHtml(row.classType)}. Damage model: ${escapeHtml(row.damageModel)}.</p>
      <p>Stock rows ignore caster offence and enemy defence. This is not classic Attack minus Defense.</p>
    </article>
  `).join("");
  const root = el(`
    <section>
      <h2>Custom hero abilities</h2>
      <p class="lede">These are buttons on the <strong>hero</strong> bar, not creature Focus buttons. Might heroes get Heroic Strike (<code>skill_warrior_ability</code>). Magic heroes get the mage commander attack (<code>skill_mage_ability</code>). Extra shouts and summons are additional SIDs. Do not overwrite the commander slot unless that is the explicit design. Stock Heroic Strike is not classic Attack-minus-Defense.</p>
      <div class="grid">${stock}</div>
      <form id="heroForm">
        ${field("heroSid", "Hero SID", "homm3_example_hero_1", "", "Machine name of one hero, not a creature.")}
        <label>Class<span class="hint">might grants Heroic Strike (skill_warrior_ability). magic grants the mage commander attack (skill_mage_ability).</span><select name="classType"><option value="might">might</option><option value="magic">magic</option></select></label>
        ${field("extraAbilitySids", "Extra ability SIDs, comma separated", "", "", "Optional extra hero buttons, such as a Warcry-like shout. Leave blank if this hero should only have the stock commander attack.")}
        <label class="check"><input type="checkbox" name="replaceCommander"> Replace the commander attack (explicit design only)</label>
        <p class="hint">Leave this unchecked unless the design is “this hero no longer has Heroic Strike / the mage commander attack.”</p>
        ${field("replacementAbilitySid", "Replacement commander SID if the box above is checked", "", "", "Required only when Replace the commander attack is checked.")}
        <button class="primary" type="submit">Write hero ability plan</button>
      </form>
      <div id="heroResult"></div>
    </section>
  `);
  root.querySelector("#heroForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const target = root.querySelector("#heroResult");
    try {
      const extras = form.extraAbilitySids.value.split(",").map((s) => s.trim()).filter(Boolean);
      const result = await postJson("/api/hero", {
        heroSid: form.heroSid.value,
        classType: form.classType.value,
        extraAbilitySids: extras,
        replaceCommander: form.replaceCommander.checked,
        replacementAbilitySid: form.replacementAbilitySid.value || null,
      });
      target.innerHTML = `${statusBox(true, `Wrote ${result.wrote}. This is a grant plan, not a complete hero row in Core.zip. The game was not changed.`)}<pre>${escapeHtml(JSON.stringify(result.plan, null, 2))}</pre>`;
    } catch (error) {
      target.innerHTML = statusBox(false, error.message);
    }
  });
  return root;
}

async function renderBuildings() {
  const meta = await getJson("/api/meta");
    const slots = meta.nativeBuildingSlots.map((slot) => {
      const rename = slot.typicalPortRename
        ? ` (HoMM3-style ports often rename this to ${slot.typicalPortRename})`
        : "";
      return `<tr><td><code>${escapeHtml(slot.nativeSid)}</code></td><td>${escapeHtml(slot.role)}</td><td>${escapeHtml(slot.displayName)}${escapeHtml(rename)}</td><td>${escapeHtml(slot.levels)}</td></tr>`;
    }).join("");
  const root = el(`
    <section>
      <h2>Custom buildings and town</h2>
      <p class="lede">The town UI already has building slots with ids such as <code>Build_Main</code> (hall) and <code>Build_Tier_1</code> (tier 1 dwelling). You rename those slots and give them bonuses. You do not create a second click system. The preferred town is an owned Unity city world where clicks stay on native building objects.</p>
      <div class="doc">
        <table>
          <tr><th>Native SID</th><th>Role</th><th>Default name</th><th>Levels</th></tr>
          ${slots}
        </table>
      </div>
      <form id="buildForm">
        ${field("factionSid", "Faction SID", "homm3_example", "", "Town identity this building list belongs to.")}
        ${field("citySid", "City SID (optional)", "homm3_example_city", "", "Machine name of the city object if you already picked one. Can match the faction plus _city.")}
        ${field("citySceneName", "Owned city scene name", "cityFactory", "", "Golden Era Unity scene-pattern name. Not “reuse vanilla Factory town.” Your real scene should be dedicated to your faction.")}
        <button class="primary" type="submit">Write building plan</button>
      </form>
      <div id="buildResult"></div>
    </section>
  `);
  root.querySelector("#buildForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target).entries());
    const target = root.querySelector("#buildResult");
    try {
      const result = await postJson("/api/buildings", data);
      target.innerHTML = `${statusBox(true, `Wrote ${result.wrote}. This lists native slots. It does not build a town scene. The game was not changed.`)}<pre>${escapeHtml(JSON.stringify(result.plan, null, 2))}</pre>`;
    } catch (error) {
      target.innerHTML = statusBox(false, error.message);
    }
  });
  return root;
}

async function renderLaws() {
  const meta = await getJson("/api/meta");
  const types = (meta.nativeLawEffectTypes || []).map((t) => `<option>${escapeHtml(t)}</option>`).join("");
  const root = el(`
    <section>
      <h2>Faction laws</h2>
      <p class="lede">A law is a bonus on the faction law tree (the point-spend chart in town), not a creature Focus button. Prefer a native table primitive such as <code>cityUnitsIncrement</code> (growth) or <code>unitStat</code> (damage percent). If this form rejects the effect type, do not invent a combat patch here. Copy parameter tokens from a vanilla law in live Core.zip.</p>
      <form id="lawForm">
        ${field("factionSid", "Faction SID", "homm3_example", "", "Town this law belongs to.")}
        ${field("lawSid", "Law SID", "homm3_example_growth", "", "Machine name of this law row. Must be unique.")}
        ${field("nameText", "Player-facing name", "Example Growth", "", "English title on the law tree.")}
        <label>Player-facing description<span class="hint">What the player should read. Describe only the bonus you will actually emit.</span><textarea name="descriptionText">Increases weekly growth for the named unit. Describe only the bonus you emit.</textarea></label>
        <label>Native effect type<span class="hint">The kind of bonus the Core table already knows. If your idea is not in this list, stop. Do not invent a combat patch in this form.</span><select name="effectType">${types}</select></label>
        ${field("parameters", "Parameters, comma separated (copy a live Core example)", "h3_example_pikeman, 1", "", "Tokens copied from a vanilla law of the same type. Example: unit SID, then the growth amount.")}
        <button class="primary" type="submit">Write native law override</button>
      </form>
      <div id="lawResult"></div>
    </section>
  `);
  root.querySelector("#lawForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target).entries());
    const target = root.querySelector("#lawResult");
    try {
      const result = await postJson("/api/laws", data);
      target.innerHTML = `${statusBox(true, `Wrote ${result.wrote}. This is one native law bonus. The game was not changed.`)}<pre>${escapeHtml(JSON.stringify(result.document, null, 2))}</pre>`;
    } catch (error) {
      target.innerHTML = statusBox(false, error.message);
    }
  });
  return root;
}

async function renderHooks() {
  const root = el(`
    <section>
      <h2>Hook catalog</h2>
      <p class="lede">A hook is a plugin patch on a method that already exists in the game. Live method names look like random letters and change after game updates. This catalog names <strong>families</strong> (selected-unit bar, town scene, icons, …) and what not to do. Golden Era class names in the catalog are examples from one plugin, not a public API. After a game patch you must re-pin names in your own plugin.</p>
      <form id="hookForm">
        ${field("q", "Search families and hooks", "", "", "Type a word such as icon, town, or ability. Leave blank and click Search to see every family.")}
        <button class="primary" type="submit">Search</button>
      </form>
      <div id="hookResults"></div>
    </section>
  `);
  async function show(query) {
    const payload = await getJson(`/api/hooks${query ? `?q=${encodeURIComponent(query)}` : ""}`);
    const target = root.querySelector("#hookResults");
    target.innerHTML = payload.results.map((row) => {
      if (row.hooks) {
        const hooks = row.hooks.map((hook) => `<li><strong>${escapeHtml(hook.name)}</strong> — ${escapeHtml(hook.do)} Do not: ${escapeHtml(hook.doNot)}</li>`).join("");
        return `<article class="card"><h3>${escapeHtml(row.title)}</h3><p>Layer: ${escapeHtml(row.layer)}. When: ${escapeHtml(row.when)}</p><p>Symbols: <code>${escapeHtml(row.symbolsClass || "")}</code></p><ul class="plain">${hooks}</ul></article>`;
      }
      return `<article class="card"><h3>${escapeHtml(row.name || row.title || "Hook")}</h3><p>${escapeHtml(row.do || JSON.stringify(row))}</p></article>`;
    }).join("");
  }
  root.querySelector("#hookForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await show(event.target.q.value);
  });
  await show("");
  return root;
}

async function renderSilent() {
  const proof = await getJson("/api/proof");
  const questions = proof.silentMiss.map((row) => `
    <button class="list-btn" data-id="${escapeHtml(row.id)}">${escapeHtml(row.prompt)}</button>
  `).join("");
  const root = el(`
    <section>
      <h2>Silent miss doctor</h2>
      <p class="lede">Use this when you believe the data is present (a JSON row, a plan dictionary, a registered patch) but the player still sees nothing. Click the sentence that matches. The answer is a diagnosis, not a second patch to paste blindly.</p>
      <div id="q">${questions}</div>
      <div id="a"></div>
    </section>
  `);
  root.querySelectorAll("button[data-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        const result = await postJson("/api/silent-miss", { id: button.dataset.id });
        root.querySelector("#a").innerHTML = `<article class="card"><h3>Diagnosis</h3><p>${escapeHtml(result.diagnosis)}</p></article>`;
      } catch (error) {
        root.querySelector("#a").innerHTML = statusBox(false, error.message);
      }
    });
  });
  return root;
}

async function renderProof() {
  const proof = await getJson("/api/proof");
  const rows = proof.tiers.map((tier) => `
    <tr>
      <td><code>${escapeHtml(tier.id)}</code></td>
      <td>${escapeHtml(tier.label)}</td>
      <td>${escapeHtml(tier.means)}</td>
      <td>${escapeHtml(tier.doesNotMean)}</td>
    </tr>
  `).join("");
  return el(`
    <section>
      <h2>Proof labels</h2>
      <p class="lede">These labels stop you from saying “it works” when you only meant “a file exists.” A generated JSON file is not the installed game. A log line that says registered is not a player seeing the button. Combat feel is a later label.</p>
      <div class="doc">
        <table>
          <tr><th>Id</th><th>Label</th><th>Means</th><th>Does not mean</th></tr>
          ${rows}
        </table>
      </div>
    </section>
  `);
}

async function renderSandbox() {
  const payload = await getJson("/api/sandbox");
  const files = payload.files.length
    ? `<ul class="plain">${payload.files.map((f) => `<li><code>${escapeHtml(f)}</code></li>`).join("")}</ul>`
    : "<p>Sandbox is empty. Use a widget to write a file.</p>";
  return el(`
    <section>
      <h2>Sandbox files</h2>
      <p>These are practice files this kit already wrote. They are not in the game. Root: <code>${escapeHtml(payload.root)}</code></p>
      ${files}
    </section>
  `);
}

window.addEventListener("hashchange", render);
render();

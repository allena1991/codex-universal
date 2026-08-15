/* Design Component runtime.
   Compiles the markup inside <x-dc> into React elements and mounts it.
   Authored pieces are the template, the Component logic class, and data-props.
   Never hand-edit a design against this file; edit the .dc.html pieces. */
(function () {
  'use strict';

  var R = window.React;
  var RD = window.ReactDOM;
  if (!R || !RD) {
    console.error('[dc] React and ReactDOM must load before support.js');
    return;
  }

  var VOID = { area: 1, base: 1, br: 1, col: 1, embed: 1, hr: 1, img: 1, input: 1, link: 1, meta: 1, param: 1, source: 1, track: 1, wbr: 1 };
  var PSEUDO = { 'style-hover': ':hover', 'style-active': ':active', 'style-focus': ':focus', 'style-before': '::before', 'style-after': '::after' };
  var HOLE = /\{\{\s*([^{}]*?)\s*\}\}/g;
  var warned = {};

  function warnOnce(msg) {
    if (warned[msg]) return;
    warned[msg] = 1;
    console.warn('[dc] ' + msg);
  }

  /* ---------- values ---------- */

  function resolve(token, scope) {
    var tok = String(token == null ? '' : token).trim();
    if (!tok) return { found: false };
    if (tok === 'true') return { found: true, value: true };
    if (tok === 'false') return { found: true, value: false };
    if (tok === 'null') return { found: true, value: null };
    if (tok === 'undefined') return { found: true, value: undefined };
    if (/^-?\d+(?:\.\d+)?$/.test(tok)) return { found: true, value: Number(tok) };
    var q = tok.charAt(0);
    if ((q === '"' || q === "'") && tok.charAt(tok.length - 1) === q) {
      return { found: true, value: tok.slice(1, -1) };
    }
    if (/[+\-*/!()[\]?:]|\s/.test(tok)) {
      warnOnce('hole "' + tok + '" is not a dotted path - compute it in renderVals()');
      return { found: false };
    }
    var parts = tok.split('.');
    var cur = scope;
    for (var i = 0; i < parts.length; i++) {
      if (cur === null || cur === undefined) return { found: false };
      var t = typeof cur;
      if (t !== 'object' && t !== 'function' && t !== 'string') return { found: false };
      if (!(parts[i] in Object(cur))) return { found: false };
      cur = Object(cur)[parts[i]];
    }
    return { found: true, value: cur };
  }

  function hasHole(str) {
    HOLE.lastIndex = 0;
    return HOLE.test(str);
  }

  function isWholeHole(str) {
    return /^\s*\{\{[^{}]*\}\}\s*$/.test(str);
  }

  function innerHole(str) {
    var m = /\{\{([^{}]*)\}\}/.exec(str);
    return m ? m[1].trim() : '';
  }

  function compileParts(str) {
    var out = [];
    var last = 0;
    var m;
    HOLE.lastIndex = 0;
    while ((m = HOLE.exec(str))) {
      if (m.index > last) out.push({ s: str.slice(last, m.index) });
      out.push({ p: m[1].trim() });
      last = m.index + m[0].length;
    }
    if (last < str.length) out.push({ s: str.slice(last) });
    return out;
  }

  function renderParts(parts, scope) {
    var s = '';
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i];
      if (p.s !== undefined) { s += p.s; continue; }
      var r = resolve(p.p, scope);
      if (!r.found) { warnOnce('unresolved hole {{ ' + p.p + ' }}'); continue; }
      if (r.value === null || r.value === undefined || r.value === false) continue;
      s += String(r.value);
    }
    return s;
  }

  /* ---------- styles ---------- */

  function cssProp(name) {
    if (name.indexOf('--') === 0) return name;
    return name.replace(/^-ms-/, 'ms-').replace(/-([a-z])/g, function (_, c) { return c.toUpperCase(); });
  }

  function parseStyle(css) {
    var out = {};
    if (!css) return out;
    var decls = String(css).split(';');
    for (var i = 0; i < decls.length; i++) {
      var d = decls[i].trim();
      if (!d) continue;
      var c = d.indexOf(':');
      if (c < 1) continue;
      var name = d.slice(0, c).trim();
      var value = d.slice(c + 1).trim();
      if (/!important$/i.test(value)) {
        value = value.replace(/\s*!important$/i, '');
        warnOnce('!important dropped from inline style "' + name + '"');
      }
      if (!name || !value) continue;
      out[cssProp(name)] = value;
    }
    return out;
  }

  var sheet = (function () {
    var el = null;
    var n = 0;
    var cache = {};
    function node() {
      if (!el) {
        el = document.createElement('style');
        el.setAttribute('data-dc-pseudo', '');
        document.head.appendChild(el);
      }
      return el;
    }
    return {
      add: function (rules) {
        var key = JSON.stringify(rules);
        if (cache[key]) return cache[key];
        var cls = 'dc-s' + (++n);
        var text = '';
        for (var i = 0; i < rules.length; i++) {
          var body = rules[i].css.trim();
          if (/^::(before|after)$/.test(rules[i].sel) && !/(^|;)\s*content\s*:/.test(body)) {
            body = "content:'';" + body;
          }
          text += '.' + cls + rules[i].sel + '{' + body + '}\n';
        }
        node().appendChild(document.createTextNode(text));
        cache[key] = cls;
        return cls;
      }
    };
  })();

  /* ---------- compile ---------- */

  var RESERVED_IMPORT = { name: 1, component: 1, 'component-from-global-scope': 1, from: 1, 'dc-props': 1 };

  /* The HTML parser lowercases attribute names, so onClick arrives as onclick and
     viewBox as viewbox. React wants the camelCase form, hence these maps. */
  var EVENT_CAMEL = ('Click DoubleClick Focus Blur FocusIn FocusOut Change Input Submit Reset ' +
    'KeyDown KeyUp KeyPress MouseDown MouseUp MouseMove MouseEnter MouseLeave MouseOver MouseOut ' +
    'ContextMenu Wheel Scroll PointerDown PointerUp PointerMove PointerEnter PointerLeave PointerCancel ' +
    'TouchStart TouchEnd TouchMove TouchCancel DragStart DragEnd DragEnter DragLeave DragOver Drag Drop ' +
    'Copy Cut Paste AnimationStart AnimationEnd AnimationIteration TransitionEnd Load Error Select Toggle ' +
    'Invalid Play Pause Ended TimeUpdate VolumeChange CanPlay Waiting Seeked Seeking Abort BeforeInput Compositionstart').split(' ');

  var NAME_MAP = { 'class': 'className', 'for': 'htmlFor' };

  (function () {
    for (var i = 0; i < EVENT_CAMEL.length; i++) {
      var camel = EVENT_CAMEL[i];
      NAME_MAP[('on' + camel).toLowerCase()] = 'on' + camel;
      NAME_MAP[('on' + camel + 'Capture').toLowerCase()] = 'on' + camel + 'Capture';
    }
    NAME_MAP.ondblclick = 'onDoubleClick';
    var camelAttrs = ('viewBox preserveAspectRatio strokeWidth strokeLinecap strokeLinejoin strokeDasharray ' +
      'strokeDashoffset strokeMiterlimit strokeOpacity fillOpacity fillRule clipPath clipRule gradientUnits ' +
      'gradientTransform patternUnits stopColor stopOpacity textAnchor dominantBaseline letterSpacing ' +
      'markerEnd markerStart markerWidth markerHeight tabIndex colSpan rowSpan maxLength minLength ' +
      'autoComplete autoFocus autoPlay srcSet useMap contentEditable spellCheck readOnly crossOrigin ' +
      'dateTime encType formAction noValidate playsInline referrerPolicy allowFullScreen').split(' ');
    for (var j = 0; j < camelAttrs.length; j++) NAME_MAP[camelAttrs[j].toLowerCase()] = camelAttrs[j];
  })();

  function reactName(name) {
    var mapped = NAME_MAP[name];
    if (mapped) return mapped;
    if (/^on[a-z]/.test(name)) {
      var camel = 'on' + name.charAt(2).toUpperCase() + name.slice(3);
      warnOnce('unknown event attribute "' + name + '" treated as ' + camel);
      return camel;
    }
    return name;
  }

  function compileAttr(name, value) {
    var rn = reactName(name);
    if (rn === 'style') {
      return hasHole(value)
        ? { name: 'style', kind: 'styleDyn', parts: compileParts(value) }
        : { name: 'style', kind: 'style', value: parseStyle(value) };
    }
    if (isWholeHole(value)) return { name: rn, kind: 'hole', path: innerHole(value) };
    if (hasHole(value)) return { name: rn, kind: 'interp', parts: compileParts(value) };
    return { name: rn, kind: 'static', value: value };
  }

  function compileAttrs(el, skip) {
    var attrs = [];
    var pseudo = [];
    for (var i = 0; i < el.attributes.length; i++) {
      var a = el.attributes[i];
      var name = a.name;
      if (PSEUDO[name]) { pseudo.push({ sel: PSEUDO[name], css: a.value }); continue; }
      if (name.indexOf('hint-') === 0) continue;
      if (skip && skip[name]) continue;
      attrs.push(compileAttr(name, a.value));
    }
    if (pseudo.length) attrs.push({ name: 'className', kind: 'static', value: sheet.add(pseudo) });
    return attrs;
  }

  function hintSize(el) {
    var v = el.getAttribute('hint-size');
    if (!v) return { width: '100%', height: '80px' };
    var p = v.split(',');
    return { width: (p[0] || '100%').trim(), height: (p[1] || '80px').trim() };
  }

  var hoisted = {};

  function hoistHelmet(el) {
    var kids = Array.prototype.slice.call(el.childNodes);
    for (var i = 0; i < kids.length; i++) {
      var n = kids[i];
      if (n.nodeType !== 1) continue;
      var tag = n.tagName.toLowerCase();
      var url = n.getAttribute('src') || n.getAttribute('href');
      if (url) {
        if (hoisted[url]) continue;
        hoisted[url] = 1;
      }
      if (tag === 'script') {
        var s = document.createElement('script');
        for (var j = 0; j < n.attributes.length; j++) s.setAttribute(n.attributes[j].name, n.attributes[j].value);
        s.textContent = n.textContent;
        document.head.appendChild(s);
      } else {
        document.head.appendChild(document.importNode(n, true));
      }
    }
  }

  function compileNodes(nodes, out) {
    out = out || [];
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      if (n.nodeType === 3) {
        var text = n.nodeValue;
        if (!text) continue;
        if (hasHole(text)) out.push({ t: 'text', parts: compileParts(text) });
        else if (text.trim() || /[ \n\t]/.test(text)) out.push({ t: 'raw', value: text });
        continue;
      }
      if (n.nodeType !== 1) continue;
      var tag = n.tagName.toLowerCase();

      if (tag === 'helmet') { hoistHelmet(n); continue; }
      if (tag === 'script') { warnOnce('<script> in a template body is ignored - put it in <helmet>'); continue; }

      if (tag === 'sc-for') {
        out.push({
          t: 'for',
          list: innerHole(n.getAttribute('list') || ''),
          as: n.getAttribute('as') || 'item',
          hintCount: parseInt(n.getAttribute('hint-placeholder-count') || '0', 10) || 0,
          children: compileNodes(n.childNodes)
        });
        continue;
      }

      if (tag === 'sc-if') {
        out.push({
          t: 'if',
          value: innerHole(n.getAttribute('value') || ''),
          hint: n.getAttribute('hint-placeholder-val') || '',
          children: compileNodes(n.childNodes)
        });
        continue;
      }

      if (tag === 'dc-import' || tag === 'x-import') {
        out.push({
          t: tag === 'dc-import' ? 'dc' : 'x',
          dcName: n.getAttribute('name') || '',
          component: n.getAttribute('component') || '',
          global: n.getAttribute('component-from-global-scope') || '',
          from: n.getAttribute('from') || '',
          spread: n.getAttribute('dc-props') ? innerHole(n.getAttribute('dc-props')) : '',
          size: hintSize(n),
          attrs: compileAttrs(n, RESERVED_IMPORT),
          children: compileNodes(n.childNodes)
        });
        continue;
      }

      out.push({
        t: 'el',
        tag: tag,
        isVoid: !!VOID[tag],
        attrs: compileAttrs(n),
        children: VOID[tag] ? [] : compileNodes(n.childNodes)
      });
    }
    return out;
  }

  /* ---------- render ---------- */

  function buildProps(attrs, scope, key) {
    var props = { key: key };
    var classes = [];
    for (var i = 0; i < attrs.length; i++) {
      var a = attrs[i];
      var v;
      if (a.kind === 'static') v = a.value;
      else if (a.kind === 'interp') v = renderParts(a.parts, scope);
      else if (a.kind === 'style') { props.style = Object.assign({}, a.value); continue; }
      else if (a.kind === 'styleDyn') { props.style = parseStyle(renderParts(a.parts, scope)); continue; }
      else {
        var r = resolve(a.path, scope);
        if (!r.found) { warnOnce('unresolved hole {{ ' + a.path + ' }} on ' + a.name); continue; }
        v = r.value;
      }
      if (a.name === 'className') { if (v) classes.push(String(v)); continue; }
      props[a.name] = v;
    }
    if (classes.length) props.className = classes.join(' ');
    return props;
  }

  function frag(key, children) {
    return R.createElement.apply(R, [R.Fragment, { key: key }].concat(children));
  }

  function renderSpecs(specs, scope, path) {
    var out = [];
    for (var i = 0; i < specs.length; i++) {
      var el = renderSpec(specs[i], scope, path + '_' + i);
      if (el !== null && el !== undefined) out.push(el);
    }
    return out;
  }

  function renderSpec(spec, scope, key) {
    switch (spec.t) {
      case 'raw':
        return spec.value;
      case 'text':
        return renderParts(spec.parts, scope);
      case 'el': {
        var props = buildProps(spec.attrs, scope, key);
        if (spec.isVoid) return R.createElement(spec.tag, props);
        return R.createElement.apply(R, [spec.tag, props].concat(renderSpecs(spec.children, scope, key)));
      }
      case 'for': {
        var r = resolve(spec.list, scope);
        var list = r.found ? r.value : null;
        var placeholder = false;
        if (list === null || list === undefined) {
          placeholder = true;
          list = new Array(spec.hintCount);
        }
        if (!Array.isArray(list)) list = Array.prototype.slice.call(list);
        var rows = [];
        for (var i = 0; i < list.length; i++) {
          var child = Object.create(scope || null);
          child[spec.as] = list[i];
          child.$index = i;
          child.$placeholder = placeholder;
          rows.push(frag(key + '_' + i, renderSpecs(spec.children, child, key + '_' + i)));
        }
        return frag(key, rows);
      }
      case 'if': {
        var rv = resolve(spec.value, scope);
        var v;
        if (rv.found) v = rv.value;
        else {
          var h = resolve(innerHole(spec.hint) || spec.hint, scope);
          v = h.found ? h.value : false;
        }
        if (!v) return null;
        return frag(key, renderSpecs(spec.children, scope, key));
      }
      case 'dc':
      case 'x': {
        var mount = buildProps(spec.attrs, scope, key);
        if (spec.spread) {
          var s = resolve(spec.spread, scope);
          if (s.found && s.value) Object.assign(mount, s.value);
        }
        var kids = renderSpecs(spec.children, scope, key);
        return R.createElement(spec.t === 'dc' ? DcHost : XHost, {
          key: key,
          spec: spec,
          mount: mount,
          kids: kids
        });
      }
      default:
        return null;
    }
  }

  /* ---------- logic class ---------- */

  function DCLogic(props) {
    R.Component.call(this, props);
  }
  DCLogic.prototype = Object.create(R.Component.prototype);
  DCLogic.prototype.constructor = DCLogic;
  DCLogic.prototype.renderVals = function () { return {}; };
  DCLogic.prototype.render = function () {
    var vals = Object.assign({}, this.props, this.renderVals() || {});
    try {
      return frag('r', renderSpecs(this.__specs || [], vals, 'r'));
    } catch (e) {
      console.error('[dc] render failed', e);
      return R.createElement('pre', { style: { color: '#b00', font: '12px ui-monospace,monospace', whiteSpace: 'pre-wrap' } }, String(e && e.stack || e));
    }
  };
  window.DCLogic = DCLogic;

  function buildComponent(templateSrc, logicSrc) {
    var tpl = document.createElement('template');
    tpl.innerHTML = templateSrc || '';
    var specs = compileNodes(tpl.content ? tpl.content.childNodes : tpl.childNodes);
    var Klass;
    if (logicSrc && /class\s+Component\b/.test(logicSrc)) {
      Klass = new Function('DCLogic', 'React', logicSrc + '\n;return Component;')(DCLogic, R);
    } else {
      Klass = function (props) { DCLogic.call(this, props); };
      Klass.prototype = Object.create(DCLogic.prototype);
      Klass.prototype.constructor = Klass;
    }
    Klass.prototype.render = DCLogic.prototype.render;
    if (!Klass.prototype.renderVals) Klass.prototype.renderVals = DCLogic.prototype.renderVals;
    Klass.prototype.__specs = specs;
    return Klass;
  }

  /* ---------- child DCs and external components ---------- */

  function placeholderEl(size, label) {
    return R.createElement('div', {
      style: {
        width: size.width, height: size.height, minHeight: size.height,
        border: '1px dashed rgba(0,0,0,.18)', borderRadius: '4px',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        font: '11px ui-monospace,Menlo,monospace', color: 'rgba(0,0,0,.35)'
      }
    }, label || '');
  }

  function errorEl(msg) {
    return R.createElement('pre', {
      style: { margin: 0, padding: '8px 10px', background: '#fff3f3', color: '#a11', font: '11px ui-monospace,Menlo,monospace', whiteSpace: 'pre-wrap' }
    }, msg);
  }

  var dcCache = {};

  function loadDc(name) {
    if (!dcCache[name]) {
      dcCache[name] = fetch(name + '.dc.html').then(function (res) {
        if (!res.ok) throw new Error('cannot load ' + name + '.dc.html (' + res.status + ')');
        return res.text();
      }).then(function (text) {
        var doc = new DOMParser().parseFromString(text, 'text/html');
        var xdc = doc.querySelector('x-dc');
        var script = doc.querySelector('script[data-dc-script]');
        return buildComponent(xdc ? xdc.innerHTML : '', script ? script.textContent : '');
      });
    }
    return dcCache[name];
  }

  var scriptCache = {};

  /* Self-registering files (web components, window globals) load as classic
     scripts; only real modules go through import(). */
  function loadScript(url) {
    if (!scriptCache[url]) {
      scriptCache[url] = new Promise(function (done, fail) {
        var el = document.createElement('script');
        el.src = url;
        el.onload = function () { done(window); };
        el.onerror = function () { fail(new Error('cannot load ' + url)); };
        document.head.appendChild(el);
      });
    }
    return scriptCache[url];
  }

  function waitFor(test, timeout) {
    var deadline = Date.now() + (timeout || 4000);
    return new Promise(function (done, fail) {
      (function tick() {
        var value = test();
        if (value) return done(value);
        if (Date.now() > deadline) return fail(new Error('timed out waiting for component to register'));
        setTimeout(tick, 40);
      })();
    });
  }

  var modCache = {};

  function loadModule(url) {
    if (!modCache[url]) {
      modCache[url] = (function () {
        if (/\.jsx(\?|$)/.test(url)) {
          return fetch(url).then(function (r) { return r.text(); }).then(function (src) {
            if (!window.Babel) throw new Error('jsx import needs Babel standalone loaded in <helmet>');
            var out = window.Babel.transform(src, { presets: ['react'] }).code;
            var mod = { exports: {} };
            new Function('module', 'exports', 'React', out)(mod, mod.exports, R);
            return Object.keys(mod.exports).length ? mod.exports : window;
          });
        }
        return import(url).catch(function (e) {
          throw new Error('cannot import ' + url + ': ' + e.message);
        });
      })();
    }
    return modCache[url];
  }

  function fromGlobal(dotted) {
    var cur = window;
    var parts = String(dotted).split('.');
    for (var i = 0; i < parts.length; i++) {
      if (!cur) return null;
      cur = cur[parts[i]];
    }
    return cur || null;
  }

  var DcHost = function (props) {
    DCLogicless.call(this, props);
    this.state = { C: null, err: null };
  };

  function DCLogicless(props) { R.Component.call(this, props); }
  DCLogicless.prototype = Object.create(R.Component.prototype);
  DCLogicless.prototype.constructor = DCLogicless;

  DcHost.prototype = Object.create(DCLogicless.prototype);
  DcHost.prototype.constructor = DcHost;
  DcHost.prototype.componentDidMount = function () {
    var self = this;
    if (!this.props.spec.dcName) return this.setState({ err: 'dc-import needs a name attribute' });
    loadDc(this.props.spec.dcName).then(function (C) { self.setState({ C: C }); },
      function (e) { self.setState({ err: String(e.message || e) }); });
  };
  DcHost.prototype.render = function () {
    if (this.state.err) return errorEl('[dc-import] ' + this.state.err);
    if (!this.state.C) return placeholderEl(this.props.spec.size, this.props.spec.dcName);
    var mount = Object.assign({}, this.props.mount);
    var style = mount.style;
    delete mount.style;
    delete mount.key;
    var el = R.createElement(this.state.C, mount);
    return style ? R.createElement('div', { style: style }, el) : el;
  };

  var XHost = function (props) {
    DCLogicless.call(this, props);
    this.state = { target: null, err: null };
  };
  XHost.prototype = Object.create(DCLogicless.prototype);
  XHost.prototype.constructor = XHost;
  function customTag(name) {
    return name && name.indexOf('-') > -1 && window.customElements && window.customElements.get(name) ? name : null;
  }

  XHost.prototype.componentDidMount = function () {
    var self = this;
    var spec = this.props.spec;
    var ready = function () { return customTag(spec.global) || fromGlobal(spec.global); };

    function settle(promise) {
      promise.then(function (target) { self.setState({ target: target }); },
        function (e) { self.setState({ err: String(e.message || e) }); });
    }

    if (spec.global) {
      if (spec.from) settle(loadScript(spec.from).then(function () { return waitFor(ready); }));
      else settle(waitFor(ready));
      return;
    }
    if (!spec.component) return this.setState({ err: 'x-import needs component or component-from-global-scope' });
    if (!spec.from) return settle(waitFor(function () { return fromGlobal(spec.component); }));
    settle(loadModule(spec.from).then(function (mod) {
      return (mod && mod[spec.component]) || fromGlobal(spec.component) ||
        Promise.reject(new Error('"' + spec.component + '" not exported by ' + spec.from));
    }));
  };
  XHost.prototype.render = function () {
    var spec = this.props.spec;
    var mount = Object.assign({}, this.props.mount);
    delete mount.key;
    if (this.state.err) return errorEl('[x-import] ' + this.state.err);
    var target = this.state.target || customTag(spec.global);
    if (!target) return placeholderEl(spec.size, spec.component || spec.global);
    return R.createElement.apply(R, [target, mount].concat(this.props.kids));
  };

  /* ---------- boot ---------- */

  function boot() {
    var xdc = document.querySelector('x-dc');
    var scriptEl = document.querySelector('script[data-dc-script]');
    if (!xdc) {
      console.error('[dc] no <x-dc> element found');
      return;
    }
    var propsMeta = {};
    var raw = scriptEl && scriptEl.getAttribute('data-props');
    if (raw) {
      try { propsMeta = JSON.parse(raw); } catch (e) { console.warn('[dc] data-props is not valid JSON'); }
    }
    var initial = {};
    Object.keys(propsMeta).forEach(function (k) {
      if (k.charAt(0) === '$') return;
      var meta = propsMeta[k];
      if (meta && typeof meta === 'object' && 'default' in meta) initial[k] = meta['default'];
    });

    var Comp = buildComponent(xdc.innerHTML, scriptEl ? scriptEl.textContent : '');
    xdc.setAttribute('hidden', '');
    xdc.style.display = 'none';

    var root = document.getElementById('dc-root');
    if (!root) {
      root = document.createElement('div');
      root.id = 'dc-root';
      document.body.insertBefore(root, xdc);
    }
    var el = R.createElement(Comp, initial);
    if (RD.createRoot) RD.createRoot(root).render(el);
    else RD.render(el, root);
    document.documentElement.setAttribute('data-dc-ready', '');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();

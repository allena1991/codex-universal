/* Minimal self-registering web component, used to exercise
   component-from-global-scope mounting in the runtime test. */
customElements.define('demo-badge', class extends HTMLElement {
  connectedCallback() {
    const tone = this.getAttribute('tone') === 'warn' ? '#8a6a1f' : '#1f4e46';
    const shadow = this.shadowRoot || this.attachShadow({ mode: 'open' });
    shadow.innerHTML =
      '<style>span{display:inline-flex;align-items:center;font:600 11px/1 ui-sans-serif,system-ui,sans-serif;' +
      'letter-spacing:.04em;text-transform:uppercase;color:#fffdf8;background:' + tone + ';padding:7px 9px;border-radius:2px}</style>' +
      '<span><slot></slot></span>';
  }
});

;(self.webpackChunktradingview = self.webpackChunktradingview || []).push([
  [1584],
  {
    67891: function (e, t) {
      var n, o, r
      ;(o = [t]),
        void 0 ===
          (r =
            'function' ==
            typeof (n = function (e) {
              'use strict'
              function t(e) {
                if (Array.isArray(e)) {
                  for (var t = 0, n = Array(e.length); t < e.length; t++)
                    n[t] = e[t]
                  return n
                }
                return Array.from(e)
              }
              Object.defineProperty(e, '__esModule', { value: !0 })
              var n = !1
              if ('undefined' != typeof window) {
                var o = {
                  get passive() {
                    n = !0
                  }
                }
                window.addEventListener('testPassive', null, o),
                  window.removeEventListener('testPassive', null, o)
              }
              var r =
                  'undefined' != typeof window &&
                  window.navigator &&
                  window.navigator.platform &&
                  /iP(ad|hone|od)/.test(window.navigator.platform),
                i = [],
                s = !1,
                a = -1,
                c = void 0,
                l = void 0,
                d = function (e) {
                  return i.some(function (t) {
                    return !(
                      !t.options.allowTouchMove || !t.options.allowTouchMove(e)
                    )
                  })
                },
                u = function (e) {
                  var t = e || window.event
                  return (
                    !!d(t.target) ||
                    1 < t.touches.length ||
                    (t.preventDefault && t.preventDefault(), !1)
                  )
                },
                h = function () {
                  setTimeout(function () {
                    void 0 !== l &&
                      ((document.body.style.paddingRight = l), (l = void 0)),
                      void 0 !== c &&
                        ((document.body.style.overflow = c), (c = void 0))
                  })
                }
              ;(e.disableBodyScroll = function (e, o) {
                if (r) {
                  if (!e)
                    return void console.error(
                      'disableBodyScroll unsuccessful - targetElement must be provided when calling disableBodyScroll on IOS devices.'
                    )
                  if (
                    e &&
                    !i.some(function (t) {
                      return t.targetElement === e
                    })
                  ) {
                    var h = { targetElement: e, options: o || {} }
                    ;(i = [].concat(t(i), [h])),
                      (e.ontouchstart = function (e) {
                        1 === e.targetTouches.length &&
                          (a = e.targetTouches[0].clientY)
                      }),
                      (e.ontouchmove = function (t) {
                        var n, o, r, i
                        1 === t.targetTouches.length &&
                          ((o = e),
                          (i = (n = t).targetTouches[0].clientY - a),
                          !d(n.target) &&
                            ((o && 0 === o.scrollTop && 0 < i) ||
                            ((r = o) &&
                              r.scrollHeight - r.scrollTop <= r.clientHeight &&
                              i < 0)
                              ? u(n)
                              : n.stopPropagation()))
                      }),
                      s ||
                        (document.addEventListener(
                          'touchmove',
                          u,
                          n ? { passive: !1 } : void 0
                        ),
                        (s = !0))
                  }
                } else {
                  ;(m = o),
                    setTimeout(function () {
                      if (void 0 === l) {
                        var e = !!m && !0 === m.reserveScrollBarGap,
                          t =
                            window.innerWidth -
                            document.documentElement.clientWidth
                        e &&
                          0 < t &&
                          ((l = document.body.style.paddingRight),
                          (document.body.style.paddingRight = t + 'px'))
                      }
                      void 0 === c &&
                        ((c = document.body.style.overflow),
                        (document.body.style.overflow = 'hidden'))
                    })
                  var v = { targetElement: e, options: o || {} }
                  i = [].concat(t(i), [v])
                }
                var m
              }),
                (e.clearAllBodyScrollLocks = function () {
                  r
                    ? (i.forEach(function (e) {
                        ;(e.targetElement.ontouchstart = null),
                          (e.targetElement.ontouchmove = null)
                      }),
                      s &&
                        (document.removeEventListener(
                          'touchmove',
                          u,
                          n ? { passive: !1 } : void 0
                        ),
                        (s = !1)),
                      (i = []),
                      (a = -1))
                    : (h(), (i = []))
                }),
                (e.enableBodyScroll = function (e) {
                  if (r) {
                    if (!e)
                      return void console.error(
                        'enableBodyScroll unsuccessful - targetElement must be provided when calling enableBodyScroll on IOS devices.'
                      )
                    ;(e.ontouchstart = null),
                      (e.ontouchmove = null),
                      (i = i.filter(function (t) {
                        return t.targetElement !== e
                      })),
                      s &&
                        0 === i.length &&
                        (document.removeEventListener(
                          'touchmove',
                          u,
                          n ? { passive: !1 } : void 0
                        ),
                        (s = !1))
                  } else
                    1 === i.length && i[0].targetElement === e
                      ? (h(), (i = []))
                      : (i = i.filter(function (t) {
                          return t.targetElement !== e
                        }))
                })
            })
              ? n.apply(t, o)
              : n) || (e.exports = r)
    },
    58644: (e) => {
      e.exports = {
        wrapper: 'wrapper-2eXD4rIf',
        input: 'input-2eXD4rIf',
        box: 'box-2eXD4rIf',
        icon: 'icon-2eXD4rIf',
        noOutline: 'noOutline-2eXD4rIf',
        'intent-danger': 'intent-danger-2eXD4rIf',
        check: 'check-2eXD4rIf',
        dot: 'dot-2eXD4rIf'
      }
    },
    64526: (e) => {
      e.exports = {
        wrap: 'wrap-164vy-kj',
        positionBottom: 'positionBottom-164vy-kj',
        backdrop: 'backdrop-164vy-kj',
        drawer: 'drawer-164vy-kj',
        positionLeft: 'positionLeft-164vy-kj'
      }
    },
    69560: (e) => {
      e.exports = {
        favorite: 'favorite-I_fAY9V2',
        disabled: 'disabled-I_fAY9V2',
        active: 'active-I_fAY9V2',
        checked: 'checked-I_fAY9V2'
      }
    },
    53400: (e, t, n) => {
      'use strict'
      n.d(t, { CheckboxInput: () => l })
      var o = n(67294),
        r = n(94184),
        i = n(49775),
        s = n(44805),
        a = n(58644),
        c = n.n(a)
      function l(e) {
        const t = r(c().box, c()['intent-' + e.intent], {
            [c().check]: !Boolean(e.indeterminate),
            [c().dot]: Boolean(e.indeterminate),
            [c().noOutline]: -1 === e.tabIndex
          }),
          n = r(c().wrapper, e.className)
        return o.createElement(
          'span',
          { className: n, title: e.title },
          o.createElement('input', {
            id: e.id,
            tabIndex: e.tabIndex,
            className: c().input,
            type: 'checkbox',
            name: e.name,
            checked: e.checked,
            disabled: e.disabled,
            value: e.value,
            autoFocus: e.autoFocus,
            role: e.role,
            onChange: function () {
              e.onChange && e.onChange(e.value)
            },
            ref: e.reference
          }),
          o.createElement(
            'span',
            { className: t },
            o.createElement(i.Icon, { icon: s, className: c().icon })
          )
        )
      }
    },
    90872: (e, t, n) => {
      'use strict'
      n.r(t), n.d(t, { ContextMenuRenderer: () => c })
      var o = n(67294),
        r = n(73935),
        i = n(56806),
        s = n(76553),
        a = n(78106)
      class c {
        constructor(e, t, n, r) {
          ;(this._root = document.createElement('div')),
            (this._isShown = !1),
            (this._manager = null),
            (this._props = {
              isOpened: !1,
              items: e,
              position: { x: 0, y: 0 },
              menuStatName: t.statName,
              mode: t.mode,
              'data-name': t['data-name']
            }),
            (this._onDestroy = n),
            (this._onShow = r),
            (this._activeElement = document.activeElement),
            (this._returnFocus = t.returnFocus),
            (this._takeFocus = t.takeFocus),
            (this._menuElementRef = o.createRef()),
            (this._doNotCloseOn = t.doNotCloseOn),
            t.manager && (this._manager = t.manager)
        }
        show(e) {
          this._onShow && this._onShow(),
            (this._isShown = !0),
            this._render({
              ...this._props,
              position: (t, n, o) => {
                var r, i, a
                e.touches &&
                  e.touches.length > 0 &&
                  (e = {
                    clientX: e.touches[0].clientX,
                    clientY: e.touches[0].clientY
                  })
                let c
                switch (
                  null !== (r = e.attachToXBy) && void 0 !== r
                    ? r
                    : (0, s.isRtl)()
                    ? 'right'
                    : 'left'
                ) {
                  case 'left':
                    c = e.clientX
                    break
                  case 'right':
                    c = e.clientX - t
                }
                let l,
                  d = null !== (i = e.attachToYBy) && void 0 !== i ? i : 'auto',
                  u = e.clientY
                if ('auto-strict' === d) {
                  const t =
                    u + (null !== (a = e.boxHeight) && void 0 !== a ? a : 0)
                  o < t + n ? (d = 'bottom') : ((d = 'top'), (u = t))
                }
                switch (d) {
                  case 'top':
                    l = Math.min(n, o - u)
                    break
                  case 'bottom':
                    ;(u -= Math.min(n, u)), (l = 0 === u ? e.clientY : void 0)
                }
                return { x: c, y: u, overrideHeight: l }
              },
              isOpened: !0,
              onClose: () => {
                this.hide(), this._unmount()
              },
              doNotCloseOn: this._doNotCloseOn,
              takeFocus: this._takeFocus,
              menuElementReference: this._menuElementRef
            })
        }
        hide() {
          ;(this._isShown = !1), this._render({ ...this._props, isOpened: !1 })
        }
        isShown() {
          return this._isShown
        }
        _unmount() {
          ;(this._isShown = !1),
            r.unmountComponentAtNode(this._root),
            this._onDestroy && this._onDestroy(),
            this._returnFocus &&
              this._activeElement instanceof HTMLElement &&
              this._activeElement.focus({ preventScroll: !0 })
        }
        _render(e) {
          r.render(
            o.createElement(
              a.SlotContext.Provider,
              { value: this._manager },
              o.createElement(i.OverlapContextMenu, { ...e })
            ),
            this._root
          )
        }
      }
    },
    59726: (e, t, n) => {
      'use strict'
      function o(e, t, n, o, r) {
        function i(r) {
          if (e > r.timeStamp) return
          const i = r.target
          void 0 !== n &&
            null !== t &&
            null !== i &&
            i.ownerDocument === o &&
            (t.contains(i) || n(r))
        }
        return (
          r.click && o.addEventListener('click', i, !1),
          r.mouseDown && o.addEventListener('mousedown', i, !1),
          r.touchEnd && o.addEventListener('touchend', i, !1),
          r.touchStart && o.addEventListener('touchstart', i, !1),
          () => {
            o.removeEventListener('click', i, !1),
              o.removeEventListener('mousedown', i, !1),
              o.removeEventListener('touchend', i, !1),
              o.removeEventListener('touchstart', i, !1)
          }
        )
      }
      n.d(t, { addOutsideEventListener: () => o })
    },
    94004: (e, t, n) => {
      'use strict'
      n.d(t, { DrawerManager: () => r, DrawerContext: () => i })
      var o = n(67294)
      class r extends o.PureComponent {
        constructor(e) {
          super(e),
            (this._addDrawer = () => {
              const e = this.state.currentDrawer + 1
              return this.setState({ currentDrawer: e }), e
            }),
            (this._removeDrawer = () => {
              const e = this.state.currentDrawer - 1
              return this.setState({ currentDrawer: e }), e
            }),
            (this.state = { currentDrawer: 0 })
        }
        render() {
          return o.createElement(
            i.Provider,
            {
              value: {
                addDrawer: this._addDrawer,
                removeDrawer: this._removeDrawer,
                currentDrawer: this.state.currentDrawer
              }
            },
            this.props.children
          )
        }
      }
      const i = o.createContext(null)
    },
    57374: (e, t, n) => {
      'use strict'
      n.d(t, { Drawer: () => v })
      var o = n(67294),
        r = n(16282),
        i = n(94184),
        s = n(67891),
        a = n(75761),
        c = n(4735),
        l = n(94004),
        d = n(43367),
        u = n(94884),
        h = n(64526)
      function v(e) {
        const {
            position: t = 'Bottom',
            onClose: n,
            children: v,
            className: m,
            theme: p = h
          } = e,
          w = (0, r.ensureNotNull)((0, o.useContext)(l.DrawerContext)),
          [f, g] = (0, o.useState)(0),
          E = (0, o.useRef)(null),
          b = (0, o.useContext)(u.CloseDelegateContext)
        return (
          (0, o.useEffect)(() => {
            const e = (0, r.ensureNotNull)(E.current)
            return (
              e.focus({ preventScroll: !0 }),
              b.subscribe(w, n),
              (0, a.setFixedBodyState)(!0),
              d.CheckMobile.iOS() && (0, s.disableBodyScroll)(e),
              g(w.addDrawer()),
              () => {
                b.unsubscribe(w, n)
                const t = w.removeDrawer()
                d.CheckMobile.iOS() && (0, s.enableBodyScroll)(e),
                  0 === t && (0, a.setFixedBodyState)(!1)
              }
            )
          }, []),
          o.createElement(
            c.Portal,
            null,
            o.createElement(
              'div',
              { className: i(h.wrap, h['position' + t]) },
              f === w.currentDrawer &&
                o.createElement('div', { className: h.backdrop, onClick: n }),
              o.createElement(
                'div',
                {
                  className: i(h.drawer, p.drawer, h['position' + t], m),
                  ref: E,
                  tabIndex: -1,
                  'data-name': e['data-name']
                },
                v
              )
            )
          )
        )
      }
    },
    65043: (e, t, n) => {
      'use strict'
      n.d(t, { FavoriteButton: () => u })
      var o = n(79881),
        r = n(67294),
        i = n(94184),
        s = n(49775),
        a = n(72579),
        c = n(23204),
        l = n(69560)
      const d = {
        add: (0, o.t)('Add to favorites'),
        remove: (0, o.t)('Remove from favorites')
      }
      function u(e) {
        const { className: t, isFilled: n, isActive: o, onClick: u, ...h } = e
        return r.createElement(s.Icon, {
          ...h,
          className: i(
            l.favorite,
            'apply-common-tooltip',
            n && l.checked,
            o && l.active,
            t
          ),
          icon: n ? a : c,
          onClick: u,
          title: n ? d.remove : d.add
        })
      }
    },
    44805: (e) => {
      e.exports =
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 11 9" width="11" height="9" fill="none"><path stroke-width="2" d="M0.999878 4L3.99988 7L9.99988 1"/></svg>'
    },
    47642: (e) => {
      e.exports =
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 16" width="10" height="16"><path d="M.6 1.4l1.4-1.4 8 8-8 8-1.4-1.4 6.389-6.532-6.389-6.668z"/></svg>'
    },
    72579: (e) => {
      e.exports =
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18" width="18" height="18" fill="none"><path fill="currentColor" d="M9 1l2.35 4.76 5.26.77-3.8 3.7.9 5.24L9 13l-4.7 2.47.9-5.23-3.8-3.71 5.25-.77L9 1z"/></svg>'
    },
    23204: (e) => {
      e.exports =
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18" width="18" height="18" fill="none"><path stroke="currentColor" d="M9 2.13l1.903 3.855.116.236.26.038 4.255.618-3.079 3.001-.188.184.044.259.727 4.237-3.805-2L9 12.434l-.233.122-3.805 2.001.727-4.237.044-.26-.188-.183-3.079-3.001 4.255-.618.26-.038.116-.236L9 2.13z"/></svg>'
    }
  }
])

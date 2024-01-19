'use strict'
;(self.webpackChunktradingview = self.webpackChunktradingview || []).push([
  [8680],
  {
    68680: (e, t, r) => {
      function i(e, t) {
        return { propType: 'checkable', properties: e, ...t }
      }
      function o(e, t, r) {
        return {
          propType: 'checkableSet',
          properties: e,
          childrenDefinitions: r,
          ...t
        }
      }
      function n(e, t) {
        return { propType: 'color', properties: e, noAlpha: !1, ...t }
      }
      r.d(t, {
        convertFromWVToDefinitionProperty: () => W,
        convertToDefinitionProperty: () => x,
        createCheckablePropertyDefinition: () => i,
        createCheckableSetPropertyDefinition: () => o,
        createColorPropertyDefinition: () => n,
        createCoordinatesPropertyDefinition: () => I,
        createEmojiPropertyDefinition: () => O,
        createLeveledLinePropertyDefinition: () => y,
        createLinePropertyDefinition: () => u,
        createNumberPropertyDefinition: () => v,
        createOptionsPropertyDefinition: () => b,
        createPropertyDefinitionsGeneralGroup: () => N,
        createPropertyDefinitionsLeveledLinesGroup: () => _,
        createRangePropertyDefinition: () => k,
        createSessionPropertyDefinition: () => A,
        createSymbolPropertyDefinition: () => z,
        createTextPropertyDefinition: () => V,
        createTransparencyPropertyDefinition: () => C,
        createTwoColorsPropertyDefinition: () => w,
        createTwoOptionsPropertyDefinition: () => T,
        destroyDefinitions: () => Z,
        getColorDefinitionProperty: () => K,
        getLockPriceScaleDefinitionProperty: () => j,
        getPriceScaleSelectionStrategyDefinitionProperty: () => G,
        getScaleRatioDefinitionProperty: () => U,
        getSymbolDefinitionProperty: () => Q,
        isPropertyDefinitionsGroup: () => X
      })
      var s = r(71172),
        p = r(33420)
      const l = [p.LINESTYLE_SOLID, p.LINESTYLE_DOTTED, p.LINESTYLE_DASHED],
        c = [1, 2, 3, 4],
        a = [s.LineEnd.Normal, s.LineEnd.Arrow]
      function u(e, t) {
        const r = { propType: 'line', properties: e, ...t }
        return (
          void 0 !== r.properties.style && (r.styleValues = l),
          void 0 !== r.properties.width && (r.widthValues = c),
          (void 0 === r.properties.leftEnd &&
            void 0 === r.properties.rightEnd) ||
            void 0 !== r.endsValues ||
            (r.endsValues = a),
          void 0 !== r.properties.value &&
            void 0 === r.valueType &&
            (r.valueType = 1),
          r
        )
      }
      const d = [p.LINESTYLE_SOLID, p.LINESTYLE_DOTTED, p.LINESTYLE_DASHED],
        f = [1, 2, 3, 4]
      function y(e, t) {
        const r = { propType: 'leveledLine', properties: e, ...t }
        return (
          void 0 !== r.properties.style && (r.styleValues = d),
          void 0 !== r.properties.width && (r.widthValues = f),
          r
        )
      }
      function v(e, t) {
        return { propType: 'number', properties: e, type: 1, ...t }
      }
      function b(e, t) {
        return { propType: 'options', properties: e, ...t }
      }
      function T(e, t) {
        return { propType: 'twoOptions', properties: e, ...t }
      }
      var g = r(79881)
      const m = [
          { id: 'bottom', value: 'bottom', title: (0, g.t)('Top') },
          { id: 'middle', value: 'middle', title: (0, g.t)('Middle') },
          { id: 'top', value: 'top', title: (0, g.t)('Bottom') }
        ],
        D = [
          { id: 'left', value: 'left', title: (0, g.t)('Left') },
          { id: 'center', value: 'center', title: (0, g.t)('Center') },
          { id: 'right', value: 'right', title: (0, g.t)('Right') }
        ],
        P = [
          {
            id: 'horizontal',
            value: 'horizontal',
            title: (0, g.t)('Horizontal')
          },
          { id: 'vertical', value: 'vertical', title: (0, g.t)('Vertical') }
        ],
        h = [10, 11, 12, 14, 16, 20, 24, 28, 32, 40].map((e) => ({
          title: String(e),
          value: e
        })),
        S = [1, 2, 3, 4],
        E = (0, g.t)('Text alignment'),
        L = (0, g.t)('Text orientation')
      function V(e, t) {
        const r = {
          propType: 'text',
          properties: e,
          ...t,
          isEditable: t.isEditable || !1
        }
        return (
          void 0 !== r.properties.size &&
            void 0 === r.sizeItems &&
            (r.sizeItems = h),
          void 0 !== r.properties.alignmentVertical &&
            void 0 === r.alignmentVerticalItems &&
            (r.alignmentVerticalItems = m),
          void 0 !== r.properties.alignmentHorizontal &&
            void 0 === r.alignmentHorizontalItems &&
            (r.alignmentHorizontalItems = D),
          (r.alignmentVerticalItems || r.alignmentHorizontalItems) &&
            void 0 === r.alignmentTitle &&
            (r.alignmentTitle = E),
          void 0 !== r.properties.orientation &&
            (void 0 === r.orientationItems && (r.orientationItems = P),
            void 0 === r.orientationTitle && (r.orientationTitle = L)),
          void 0 !== r.properties.borderWidth &&
            void 0 === r.borderWidthItems &&
            (r.borderWidthItems = S),
          r
        )
      }
      function w(e, t) {
        return {
          propType: 'twoColors',
          properties: e,
          noAlpha1: !1,
          noAlpha2: !1,
          ...t
        }
      }
      function I(e, t) {
        return { propType: 'coordinates', properties: e, ...t }
      }
      function k(e, t) {
        return { propType: 'range', properties: e, ...t }
      }
      function C(e, t) {
        return { propType: 'transparency', properties: e, ...t }
      }
      function z(e, t) {
        return { propType: 'symbol', properties: e, ...t }
      }
      function A(e, t) {
        return { propType: 'session', properties: e, ...t }
      }
      function O(e, t) {
        return { propType: 'emoji', properties: e, ...t }
      }
      var H = r(32856),
        M = r.n(H)
      function N(e, t, r) {
        return {
          id: t,
          title: r,
          groupType: 'general',
          definitions: new (M())(e)
        }
      }
      function _(e, t, r) {
        return {
          id: t,
          title: r,
          groupType: 'leveledLines',
          definitions: new (M())(e)
        }
      }
      function Y(e, t, r) {
        const i = new Map(),
          o = void 0 !== t ? t[0] : (e) => e,
          n = void 0 !== t ? (void 0 !== t[1] ? t[1] : t[0]) : (e) => e,
          s = {
            value: () => o(e.value()),
            setValue: (t) => {
              e.setValue(n(t))
            },
            subscribe: (t, r) => {
              const o = (e) => {
                r(s)
              }
              i.set(r, o), e.subscribe(t, o)
            },
            unsubscribe: (t, r) => {
              const o = i.get(r)
              o && (e.unsubscribe(t, o), i.delete(r))
            },
            unsubscribeAll: (t) => {
              e.unsubscribeAll(t), i.clear()
            },
            destroy: () => {
              null == r || r()
            }
          }
        return s
      }
      function x(e, t, r, i, o, n) {
        const s = Y(t, i, n),
          p = void 0 !== i ? (void 0 !== i[1] ? i[1] : i[0]) : (e) => e
        return (
          (s.setValue = null != o ? o : (i) => e.setProperty(t, p(i), r)), s
        )
      }
      function R(e, t) {
        const r = new Map(),
          i = void 0 !== t ? t[0] : (e) => e,
          o = void 0 !== t ? (void 0 !== t[1] ? t[1] : t[0]) : (e) => e,
          n = {
            value: () => i(e.value()),
            setValue: (t) => {
              e.setValue(o(t))
            },
            subscribe: (t, i) => {
              const o = () => {
                i(n)
              }
              let s = r.get(t)
              void 0 === s
                ? ((s = new Map()), s.set(i, o), r.set(t, s))
                : s.set(i, o),
                e.subscribe(o)
            },
            unsubscribe: (t, i) => {
              const o = r.get(t)
              if (void 0 !== o) {
                const t = o.get(i)
                void 0 !== t && (e.unsubscribe(t), o.delete(i))
              }
            },
            unsubscribeAll: (t) => {
              const i = r.get(t)
              void 0 !== i &&
                (i.forEach((t, r) => {
                  e.unsubscribe(t)
                }),
                i.clear())
            }
          }
        return n
      }
      function W(e, t, r, i) {
        const o = R(t, i),
          n = void 0 !== i ? (void 0 !== i[1] ? i[1] : i[0]) : (e) => e
        return (o.setValue = (i) => e.setWatchedValue(t, n(i), r)), o
      }
      function G(e, t) {
        const r = Y(t)
        return (r.setValue = (t) => e.setPriceScaleSelectionStrategy(t)), r
      }
      function j(e, t, r, i) {
        const o = Y(t)
        return (
          (o.setValue = (t) => {
            const o = { lockScale: t }
            e.setPriceScaleMode(o, r, i)
          }),
          o
        )
      }
      function U(e, t, r, i) {
        const o = Y(t, i)
        return (
          (o.setValue = (i) => {
            e.setScaleRatioProperty(t, i, r)
          }),
          o
        )
      }
      var B = r(14563),
        F = r(50968),
        q = r(69881)
      function J(e, t) {
        if ((0, F.isHexColor)(e)) {
          const r = (0, B.parseRgb)(e)
          return (0, B.rgbaToString)((0, B.rgba)(r, (100 - t) / 100))
        }
        return e
      }
      function K(e, t, r, i, o) {
        let n
        if (null !== r) {
          n = (function (e) {
            const t = Y(e)
            return (
              (t.destroy = () => {
                e.destroy()
              }),
              t
            )
          })((0, q.combineProperty)(J, t, r))
        } else n = Y(t, [() => J(t.value(), 0), (e) => e])
        return (
          (n.setValue = (r) => {
            o && e.beginUndoMacro(i),
              e.setProperty(t, r, i),
              o && e.endUndoMacro()
          }),
          n
        )
      }
      function Q(e, t, r, i, o, n) {
        const s = [
          ((p = r),
          (l = t),
          (e) => {
            const t = p(l)
            if (e === l.value() && null !== t) {
              const e = t.ticker || t.full_name
              if (e) return e
            }
            return e
          }),
          (e) => e
        ]
        var p, l
        const c = x(e, t, o, s)
        n && (c.setValue = n)
        const a = new Map()
        ;(c.subscribe = (e, r) => {
          const i = (e) => {
            r(c)
          }
          a.set(r, i), t.subscribe(e, i)
        }),
          (c.unsubscribe = (e, r) => {
            const i = a.get(r)
            i && (t.unsubscribe(e, i), a.delete(r))
          })
        const u = {}
        return (
          i.subscribe(u, () => {
            a.forEach((e, t) => {
              t(c)
            })
          }),
          (c.destroy = () => {
            i.unsubscribeAll(u), a.clear()
          }),
          c
        )
      }
      function X(e) {
        return e.hasOwnProperty('groupType')
      }
      function Z(e) {
        e.forEach((e) => {
          if (e.hasOwnProperty('propType')) {
            Object.keys(e.properties).forEach((t) => {
              const r = e.properties[t]
              void 0 !== r && void 0 !== r.destroy && r.destroy()
            })
          } else Z(e.definitions.value())
        })
      }
    }
  }
])

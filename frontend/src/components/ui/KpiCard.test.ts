import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import KpiCard from './KpiCard.vue'

describe('KpiCard', () => {
  it('renders label text', () => {
    const wrapper = mount(KpiCard, { props: { label: 'งบประมาณรวม', value: 0 } })
    expect(wrapper.text()).toContain('งบประมาณรวม')
  })

  it('renders formatted value in the value element', () => {
    const wrapper = mount(KpiCard, { props: { label: 'ยอด', value: 0 } })
    expect(wrapper.find('.text-2xl').exists()).toBe(true)
  })

  it('prepends prefix and appends suffix to value', () => {
    const wrapper = mount(KpiCard, {
      props: { label: 'ยอด', value: 100, prefix: '฿', suffix: ' บาท' },
    })
    const text = wrapper.find('.text-2xl').text()
    expect(text.startsWith('฿')).toBe(true)
    expect(text.endsWith('บาท')).toBe(true)
  })

  it('applies default color class text-fg to value element', () => {
    const wrapper = mount(KpiCard, { props: { label: 'ยอด', value: 0 } })
    expect(wrapper.find('.text-2xl').classes()).toContain('text-fg')
  })

  it('applies custom color class to value element', () => {
    const wrapper = mount(KpiCard, {
      props: { label: 'ยอด', value: 0, color: 'text-success' },
    })
    expect(wrapper.find('.text-2xl').classes()).toContain('text-success')
  })

  it('renders sub text when provided', () => {
    const wrapper = mount(KpiCard, {
      props: { label: 'ยอด', value: 0, sub: 'เทียบกับปีที่แล้ว' },
    })
    expect(wrapper.text()).toContain('เทียบกับปีที่แล้ว')
  })

  it('does not render sub element when prop is omitted', () => {
    const wrapper = mount(KpiCard, { props: { label: 'ยอด', value: 0 } })
    expect(wrapper.findAll('.text-xs').some(el => el.text().includes('เทียบ'))).toBe(false)
  })
})

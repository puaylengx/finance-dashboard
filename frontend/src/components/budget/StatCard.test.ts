import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatCard from './StatCard.vue'

const BASE = { label: 'งบประมาณ', value: '1,500,000.00', unit: 'บาท' }

describe('StatCard', () => {
  it('renders label, value, and unit', () => {
    const wrapper = mount(StatCard, { props: BASE })
    expect(wrapper.text()).toContain('งบประมาณ')
    expect(wrapper.text()).toContain('1,500,000.00')
    expect(wrapper.text()).toContain('บาท')
  })

  it('renders subValue when provided', () => {
    const wrapper = mount(StatCard, { props: { ...BASE, subValue: 'เพิ่มขึ้น 5%' } })
    expect(wrapper.text()).toContain('เพิ่มขึ้น 5%')
  })

  it('does not render subValue element when omitted', () => {
    const wrapper = mount(StatCard, { props: BASE })
    expect(wrapper.text()).not.toContain('เพิ่มขึ้น')
  })

  it('applies indigo colorMap classes by default', () => {
    const wrapper = mount(StatCard, { props: BASE })
    expect(wrapper.html()).toContain('bg-indigo-500')
  })

  it('applies emerald colorMap classes when color=emerald', () => {
    const wrapper = mount(StatCard, { props: { ...BASE, color: 'emerald' } })
    expect(wrapper.html()).toContain('bg-emerald-500')
    expect(wrapper.html()).not.toContain('bg-indigo-500')
  })

  it('renders icon slot content inside icon container', () => {
    const wrapper = mount(StatCard, {
      props: BASE,
      slots: { icon: '<span data-testid="custom-icon">★</span>' },
    })
    expect(wrapper.find('[data-testid="custom-icon"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="custom-icon"]').text()).toBe('★')
  })
})

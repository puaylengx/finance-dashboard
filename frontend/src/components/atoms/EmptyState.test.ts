import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EmptyState from './EmptyState.vue'

describe('EmptyState', () => {
  it('defaults to no-data variant with correct title and description', () => {
    const wrapper = mount(EmptyState)
    expect(wrapper.find('h3').text()).toBe('ยังไม่มีข้อมูล')
    expect(wrapper.find('p').text()).toContain('ยังไม่มีข้อมูล')
  })

  it('no-results variant shows correct title', () => {
    const wrapper = mount(EmptyState, { props: { variant: 'no-results' } })
    expect(wrapper.find('h3').text()).toBe('ไม่พบข้อมูล')
  })

  it('no-permission variant shows correct title', () => {
    const wrapper = mount(EmptyState, { props: { variant: 'no-permission' } })
    expect(wrapper.find('h3').text()).toBe('ไม่มีสิทธิ์เข้าถึง')
  })

  it('custom title prop overrides variant default', () => {
    const wrapper = mount(EmptyState, { props: { title: 'หัวข้อกำหนดเอง' } })
    expect(wrapper.find('h3').text()).toBe('หัวข้อกำหนดเอง')
  })

  it('custom description prop overrides variant default', () => {
    const wrapper = mount(EmptyState, { props: { description: 'คำอธิบายกำหนดเอง' } })
    expect(wrapper.find('p').text()).toBe('คำอธิบายกำหนดเอง')
  })

  it('renders action slot content when provided', () => {
    const wrapper = mount(EmptyState, {
      slots: { action: '<button>ลองอีกครั้ง</button>' },
    })
    expect(wrapper.find('button').exists()).toBe(true)
    expect(wrapper.find('button').text()).toBe('ลองอีกครั้ง')
  })

  it('does not render action container when slot is not provided', () => {
    const wrapper = mount(EmptyState)
    expect(wrapper.find('button').exists()).toBe(false)
  })
})

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SkeletonCard from './SkeletonCard.vue'

describe('SkeletonCard', () => {
  it('renders with default height of 80px', () => {
    const wrapper = mount(SkeletonCard)
    expect((wrapper.element as HTMLElement).style.height).toBe('80px')
  })

  it('accepts custom height via prop', () => {
    const wrapper = mount(SkeletonCard, { props: { height: '200px' } })
    expect((wrapper.element as HTMLElement).style.height).toBe('200px')
  })

  it('applies animate-skeleton class', () => {
    const wrapper = mount(SkeletonCard)
    expect(wrapper.classes()).toContain('animate-skeleton')
  })
})

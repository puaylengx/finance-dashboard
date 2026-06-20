import { apiClient } from './client'
import type { ApiResponse, ApiPageResponse, FinancePayload, IoPayload, FinanceQueryParams, IoQueryParams, CoordinatorResponse } from '@/types/api'

const BASE = '/api/v1'

function toParams(p: Record<string, unknown>): Record<string, string> {
  return Object.fromEntries(
    Object.entries(p)
      .filter(([, v]) => v !== undefined && v !== null && v !== '')
      .map(([k, v]) => [k, String(v)]),
  )
}

export async function fetchFinance(params: FinanceQueryParams): Promise<FinancePayload> {
  const { data } = await apiClient.get<ApiResponse<FinancePayload>>(`${BASE}/finance`, { params: toParams(params as Record<string, unknown>) })
  return data.data
}

export async function fetchBudget(params: FinanceQueryParams): Promise<FinancePayload> {
  const { data } = await apiClient.get<ApiResponse<FinancePayload>>(`${BASE}/budget`, { params: toParams(params as Record<string, unknown>) })
  return data.data
}

export async function fetchIO(params: IoQueryParams): Promise<IoPayload> {
  const { data } = await apiClient.get<ApiResponse<IoPayload>>(`${BASE}/io`, { params: toParams(params as Record<string, unknown>) })
  return data.data
}

export async function fetchCoordinators(): Promise<CoordinatorResponse[]> {
  const { data } = await apiClient.get<ApiPageResponse<CoordinatorResponse>>(`${BASE}/admin/coordinators`)
  return data.data
}

export async function addCoordinator(username: string): Promise<CoordinatorResponse> {
  const { data } = await apiClient.post<ApiResponse<CoordinatorResponse>>(`${BASE}/admin/coordinators`, { username })
  return data.data
}

export async function toggleCoordinator(id: number): Promise<CoordinatorResponse> {
  const { data } = await apiClient.patch<ApiResponse<CoordinatorResponse>>(`${BASE}/admin/coordinators/${id}`)
  return data.data
}

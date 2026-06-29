import { apiClient } from './client'
import type { ApiResponse, TokenResponse, DraftLoginRequest, UserInfo } from '@/types/api'

const BASE = '/api/v1/auth'

export async function draftLogin(payload: DraftLoginRequest): Promise<TokenResponse> {
  const { data } = await apiClient.post<ApiResponse<TokenResponse>>(`${BASE}/draft-login`, payload)
  return data.data
}

export async function entraLogin(accessToken: string, jobTitle = ''): Promise<TokenResponse> {
  const { data } = await apiClient.post<ApiResponse<TokenResponse>>(`${BASE}/entra-login`, {
    access_token: accessToken,
    job_title: jobTitle,
  })
  return data.data
}

export async function fetchMe(): Promise<UserInfo> {
  const { data } = await apiClient.get<ApiResponse<UserInfo>>(`${BASE}/me`)
  return data.data
}

// Backend response envelope
export interface ApiResponse<T> { success: boolean; data: T }
export interface ApiPageResponse<T> {
  success: boolean; data: T[]
  page: number; page_size: number; total: number; total_pages: number
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export interface TokenResponse {
  token: string; token_type: string; expires_in: number
  role: string; position: string | null; coordinator: boolean; name: string
}
export interface UserInfo {
  username: string; role: string; position: string | null
  coordinator: boolean; expires_at: string | null
}
export interface DraftLoginRequest { job_title: string; name: string }

// ── Budget ────────────────────────────────────────────────────────────────────
export interface BudgetKpis {
  total_amount: number; total_budget: number
  doc_count: number; avg_amount_per_doc: number
}
export interface TrendMonthItem {
  month: string; month_number: number; fiscal_month: number
  pa_month: number; pa_year: number; total: number
}
export interface GlItem { gl_id: string; gl_description: string; gl_group: string; total: number }
export interface CostCenterItem {
  cost_center_eng: string; cost_center_description: string; total: number
}
export interface DetailsBreakdownItem { details: string; amount: number }
export interface PivotGlItem {
  gl_id: string; gl_description: string
  total_amount: number; details_breakdown: DetailsBreakdownItem[]
}
export interface BudgetPayload {
  kpis: BudgetKpis; trend_month: TrendMonthItem[]
  table_by_gl: GlItem[]; table_by_cost_center: CostCenterItem[]
  pivot_table_by_gl_detail: PivotGlItem[]
  table_by_gl_division: GlItem[]; table_by_cost_center_division: CostCenterItem[]
  pivot_table_by_gl_detail_division: PivotGlItem[]
  table_by_gl_all: GlItem[]; table_by_cost_center_all: CostCenterItem[]
  pivot_table_by_gl_detail_all: PivotGlItem[]
}

// ── IO ────────────────────────────────────────────────────────────────────────
export interface IoKpis {
  total_amount: number; total_budget: number
  total_amount_io_goods: number; count_io_goods: number
  total_amount_io_project: number; count_io_project: number
}
export interface SpendingItem {
  cost_center_eng: string; cost_center_description: string; total: number
}
export interface IoOrderBreakdownItem { order_description: string; details: string; amount: number }
export interface IoGoodsItem {
  io_goods: string; io_goods_description: string
  total_amount: number; order_breakdown: IoOrderBreakdownItem[]
}
export interface IoProjectItem {
  io_project: string; io_project_description: string
  total_amount: number; order_breakdown: IoOrderBreakdownItem[]
}
export interface IoWorkItem {
  io_work: string; io_work_description: string
  total_amount: number; order_breakdown: IoOrderBreakdownItem[]
}
export interface IoPayload {
  kpis: IoKpis
  spending_by_dept: SpendingItem[]; spending_by_division: SpendingItem[]
  pivot_table_by_io_goods: IoGoodsItem[]
  pivot_table_by_io_project: IoProjectItem[]
  pivot_table_by_io_work: IoWorkItem[]
}

// ── Query Params ─────────────────────────────────────────────────────────────
export interface BudgetQueryParams {
  year?: number; pa_year?: number; month_from?: number; month_to?: number
  gl_group?: string; cost_center?: string; cost_owner?: string; q?: string
}
export interface IoQueryParams {
  year?: number; pa_year?: number; month_from?: number; month_to?: number
  cost_center?: string; cost_owner?: string; q?: string
}

// ── Admin ─────────────────────────────────────────────────────────────────────
export interface CoordinatorResponse {
  id: number; username: string; active: boolean
  created_at: string | null; updated_at: string | null
  created_by: string | null; updated_by: string | null
}

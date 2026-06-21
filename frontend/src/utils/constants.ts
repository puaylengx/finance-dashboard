export const FISCAL_MONTHS: { value: number; label: string }[] = [
  { value: 1,  label: 'October'   },
  { value: 2,  label: 'November'  },
  { value: 3,  label: 'December'  },
  { value: 4,  label: 'January'   },
  { value: 5,  label: 'February'  },
  { value: 6,  label: 'March'     },
  { value: 7,  label: 'April'     },
  { value: 8,  label: 'May'       },
  { value: 9,  label: 'June'      },
  { value: 10, label: 'July'      },
  { value: 11, label: 'August'    },
  { value: 12, label: 'September' },
]

export const PA_MONTHS: { value: number; label: string }[] = [
  { value: 1,  label: 'July'      },
  { value: 2,  label: 'August'    },
  { value: 3,  label: 'September' },
  { value: 4,  label: 'October'   },
  { value: 5,  label: 'November'  },
  { value: 6,  label: 'December'  },
  { value: 7,  label: 'January'   },
  { value: 8,  label: 'February'  },
  { value: 9,  label: 'March'     },
  { value: 10, label: 'April'     },
  { value: 11, label: 'May'       },
  { value: 12, label: 'June'      },
]

export const fiscalMonthLabel = (v: number): string =>
  FISCAL_MONTHS.find(m => m.value === v)?.label ?? ''

export const paMonthLabel = (v: number): string =>
  PA_MONTHS.find(m => m.value === v)?.label ?? ''

export const DIVISION_COLORS = [
  '#2563eb', '#10b981', '#eab308', '#06b6d4', '#14b8a6',
  '#6366f1', '#ec4899', '#8b5cf6', '#f97316', '#64748b',
]

export const DEPT_COLORS = [
  '#8b5cf6', '#ec4899', '#eab308', '#14b8a6', '#f97316',
  '#10b981', '#6366f1', '#2563eb', '#06b6d4', '#64748b',
]
